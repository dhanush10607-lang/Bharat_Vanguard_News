"""
Bharat Vanguard News (BVN) — OAuth Router (Google Login via Supabase Auth)

How this works:
──────────────────────────────────────────────────────────────
  1. Frontend calls GET /api/v1/auth/google
     → Backend returns the Supabase Google OAuth URL

  2. User is redirected to Google's consent screen

  3. Google redirects to Supabase's callback URL
     (https://[project].supabase.co/auth/v1/callback)

  4. Supabase exchanges the code for tokens,
     creates/updates the user in Supabase Auth,
     then redirects to your frontend:
     (https://yourapp.vercel.app/auth/callback?access_token=...)

  5. Frontend sends the Supabase access_token to:
     POST /api/v1/auth/google/verify
     → Backend verifies the token, syncs user to our DB,
       returns our own app JWT

  6. Frontend stores our JWT and uses it for all API calls
──────────────────────────────────────────────────────────────

Setup (one-time, ~5 minutes):
  1. Google Cloud Console → Create OAuth 2.0 Client
     - Authorized redirect: https://[ref].supabase.co/auth/v1/callback
  2. Supabase Dashboard → Authentication → Providers → Google
     - Paste Client ID and Secret
  3. Add GOOGLE_CLIENT_ID, SUPABASE_JWT_SECRET to your .env
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from jose import jwt, JWTError
import httpx

from shared.database import get_db
from shared.models import User, UserRole
from shared.config import settings
from apps.api.routers.users import create_token, hash_password

router = APIRouter()


# ============================================================
#  SCHEMAS
# ============================================================

class OAuthTokenRequest(BaseModel):
    """The Supabase access_token sent by the frontend after OAuth redirect."""
    access_token: str


class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


# ============================================================
#  HELPERS
# ============================================================

async def decode_supabase_token(token: str) -> dict:
    """
    Verify and decode a Supabase Auth JWT.
    Supabase signs JWTs with the JWT Secret found in:
    Supabase Dashboard → Settings → API → JWT Secret
    """
    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=500,
            detail="SUPABASE_JWT_SECRET not configured on server",
        )
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},   # Supabase tokens use "authenticated" audience
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Supabase token: {e}",
        )


async def get_or_create_oauth_user(
    db: AsyncSession,
    email: str,
    display_name: str,
    avatar_url: Optional[str],
    provider: str,
    provider_id: str,
) -> User:
    """
    Find existing user by email OR create a new one from OAuth data.
    Links provider account if user already exists with this email.
    """
    # Try to find by OAuth provider ID first (most precise)
    result = await db.execute(
        select(User).where(
            User.oauth_provider == provider,
            User.oauth_provider_id == provider_id,
        )
    )
    user = result.scalar_one_or_none()

    if user:
        # Update avatar in case it changed
        if avatar_url:
            user.avatar_url = avatar_url
        user.last_login = datetime.now(timezone.utc)
        return user

    # Try to find by email (user may have registered with email/password before)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # Link this Google account to existing user
        user.oauth_provider = provider
        user.oauth_provider_id = provider_id
        if avatar_url:
            user.avatar_url = avatar_url
        user.last_login = datetime.now(timezone.utc)
        return user

    # Create brand new user from Google data
    # Generate a safe username from the display name
    base_username = email.split("@")[0].lower().replace(".", "_")[:30]
    username = base_username

    # Ensure username uniqueness
    counter = 2
    while True:
        exists = await db.execute(select(User).where(User.username == username))
        if not exists.scalar_one_or_none():
            break
        username = f"{base_username}{counter}"
        counter += 1

    user = User(
        email=email,
        username=username,
        display_name=display_name or email.split("@")[0],
        password_hash=None,           # OAuth users have no password
        oauth_provider=provider,
        oauth_provider_id=provider_id,
        avatar_url=avatar_url,
        role=UserRole.READER,
        is_verified=True,             # Google already verified their email
        last_login=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    return user


# ============================================================
#  ENDPOINTS
# ============================================================

@router.get("/google")
async def google_login_url():
    """
    Returns the Supabase Google OAuth URL.
    Frontend should redirect the user to this URL.
    """
    if not settings.supabase_url:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    oauth_url = (
        f"{settings.supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={settings.oauth_redirect_url}"
    )
    return {
        "oauth_url": oauth_url,
        "provider": "google",
        "instructions": "Redirect the user to oauth_url to begin Google login",
    }


@router.get("/google/redirect")
async def google_login_redirect():
    """
    Direct redirect to Google OAuth (for server-side flows).
    The browser will be sent directly to the Google consent screen.
    """
    if not settings.supabase_url:
        raise HTTPException(status_code=500, detail="Supabase not configured")

    oauth_url = (
        f"{settings.supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={settings.oauth_redirect_url}"
    )
    return RedirectResponse(url=oauth_url)


@router.post("/google/verify", response_model=OAuthTokenResponse)
async def verify_google_token(
    body: OAuthTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Called by the frontend AFTER the Google OAuth flow completes.

    Flow:
      1. User completes Google login on Supabase's OAuth page
      2. Supabase redirects to frontend /auth/callback with access_token
      3. Frontend POSTs the access_token to this endpoint
      4. We verify it, sync user to our DB, return our own app JWT

    This is the "handshake" between Supabase Auth and our app's user system.
    """
    # Step 1: Decode and verify the Supabase JWT
    payload = await decode_supabase_token(body.access_token)

    # Step 2: Extract user info from the token
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Token missing email claim")

    # Supabase stores user metadata under app_metadata or user_metadata
    user_metadata = payload.get("user_metadata", {})
    display_name = (
        user_metadata.get("full_name")
        or user_metadata.get("name")
        or email.split("@")[0]
    )
    avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")
    provider_id = payload.get("sub", "")    # Supabase user UUID

    # Step 3: Sync to our users table
    user = await get_or_create_oauth_user(
        db=db,
        email=email,
        display_name=display_name,
        avatar_url=avatar_url,
        provider="google",
        provider_id=provider_id,
    )

    # Step 4: Issue our own app JWT
    app_token = create_token(str(user.user_id))

    return OAuthTokenResponse(
        access_token=app_token,
        expires_in=settings.jwt_expire_minutes * 60,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "display_name": user.display_name,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "role": user.role.value,
        },
    )


@router.get("/providers")
async def list_auth_providers():
    """Lists which auth providers are configured on this instance."""
    return {
        "providers": {
            "email_password": True,
            "google": bool(settings.google_client_id and settings.supabase_jwt_secret),
        },
        "google_configured": bool(settings.google_client_id),
    }
