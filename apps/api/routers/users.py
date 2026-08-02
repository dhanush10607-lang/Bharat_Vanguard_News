"""
Bharat Vanguard News (BVN) — Users Router
Authentication (register, login, profile) and user preferences.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import JWTError, jwt

from shared.database import get_db
from shared.models import User, UserRole, UserBookmark, UserLike, Article
from shared.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


# ============================================================
#  SCHEMAS
# ============================================================

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    display_name: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    user_id: UUID
    email: str
    username: str
    display_name: Optional[str]
    role: str
    preferences: Optional[dict]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================
#  HELPERS
# ============================================================

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT auth dependency — validates token and returns current user."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_error
    except JWTError:
        raise credentials_error

    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_error

    return user


# ============================================================
#  ENDPOINTS
# ============================================================

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check email/username uniqueness
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=data.email,
        username=data.username,
        display_name=data.display_name or data.username,
        password_hash=hash_password(data.password),
        role=UserRole.READER,
    )
    db.add(user)
    await db.flush()

    token = create_token(str(user.user_id))
    return TokenResponse(access_token=token, expires_in=settings.jwt_expire_minutes * 60)


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Login with email + password. Returns JWT token."""
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    user.last_login = datetime.now(timezone.utc)
    token = create_token(str(user.user_id))
    return TokenResponse(access_token=token, expires_in=settings.jwt_expire_minutes * 60)


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's profile."""
    return UserProfile(
        user_id=current_user.user_id,
        email=current_user.email,
        username=current_user.username,
        display_name=current_user.display_name,
        role=current_user.role.value,
        preferences=current_user.preferences,
        created_at=current_user.created_at,
    )


@router.put("/me/preferences")
async def update_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user news preferences (categories, countries, etc.)"""
    current_user.preferences = preferences
    return {"message": "Preferences updated", "preferences": preferences}


# ============================================================
#  BOOKMARKS
# ============================================================

@router.get("/bookmarks/articles")
async def get_bookmarked_articles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all article UUIDs bookmarked by the user."""
    result = await db.execute(
        select(UserBookmark.article_id).where(
            UserBookmark.user_id == current_user.user_id,
            UserBookmark.article_id.isnot(None)
        )
    )
    article_ids = result.scalars().all()
    return {"bookmarked_article_ids": [str(aid) for aid in article_ids]}


@router.get("/bookmarks/details")
async def get_bookmarked_articles_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the full article objects for all bookmarks of the user."""
    # Note: for a large number of bookmarks, this should be paginated
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.publisher))
        .join(UserBookmark, UserBookmark.article_id == Article.article_id)
        .where(UserBookmark.user_id == current_user.user_id)
        .order_by(UserBookmark.created_at.desc())
        .limit(50)
    )
    articles = result.scalars().all()
    
    # We must convert to dicts to match what the frontend expects
    from apps.api.routers.articles import ArticleListItem
    articles_out = [ArticleListItem.model_validate(a) for a in articles]
    return {"items": articles_out}


@router.post("/bookmarks/articles/{article_id}")
async def toggle_article_bookmark(
    article_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a bookmark for an article."""
    result = await db.execute(
        select(UserBookmark).where(
            UserBookmark.user_id == current_user.user_id,
            UserBookmark.article_id == article_id
        )
    )
    existing_bookmarks = result.scalars().all()
    
    if existing_bookmarks:
        for bk in existing_bookmarks:
            await db.delete(bk)
        return {"status": "removed", "article_id": str(article_id)}
    else:
        new_bookmark = UserBookmark(
            user_id=current_user.user_id,
            article_id=article_id
        )
        db.add(new_bookmark)
        return {"status": "added", "article_id": str(article_id)}

# ============================================================
#  LIKES
# ============================================================

@router.get("/likes/articles")
async def get_liked_articles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all article UUIDs liked by the user."""
    result = await db.execute(
        select(UserLike.article_id).where(
            UserLike.user_id == current_user.user_id,
            UserLike.article_id.isnot(None)
        )
    )
    article_ids = result.scalars().all()
    return {"liked_article_ids": [str(aid) for aid in article_ids]}


@router.post("/likes/articles/{article_id}")
async def toggle_article_like(
    article_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a like for an article and update the article's like_count."""
    result = await db.execute(
        select(UserLike).where(
            UserLike.user_id == current_user.user_id,
            UserLike.article_id == article_id
        )
    )
    existing_likes = result.scalars().all()
    
    # Fetch the article to update its likes_count
    article_result = await db.execute(select(Article).where(Article.article_id == article_id))
    article = article_result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if existing_likes:
        for like_obj in existing_likes:
            await db.delete(like_obj)
            
        if article.likes_count and article.likes_count > 0:
            # We decrement by 1 conceptually, even if there were duplicate records
            article.likes_count -= 1
            
        return {"status": "removed", "article_id": str(article_id)}
    else:
        new_like = UserLike(
            user_id=current_user.user_id,
            article_id=article_id
        )
        db.add(new_like)
        if article.likes_count is None:
            article.likes_count = 1
        else:
            article.likes_count += 1
        return {"status": "added", "article_id": str(article_id)}
