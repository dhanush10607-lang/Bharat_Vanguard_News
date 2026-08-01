# Google OAuth Setup Guide

> **Time required**: ~5–10 minutes
> **Cost**: Free
> **Prerequisites**: A Google account

---

## Why Supabase Auth?

Since TruthLens AI already uses Supabase as its database, we use **Supabase Auth** to handle the Google OAuth flow. This means:
- ✅ No extra service or cost
- ✅ Supabase handles the Google redirect and token exchange
- ✅ Our backend just verifies the result

---

## Step 1 — Create a Google OAuth App

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth 2.0 Client ID**
5. Choose **Web application**
6. Set the name to `TruthLens AI`
7. Under **Authorized redirect URIs**, add:
   ```
   https://[YOUR_PROJECT_REF].supabase.co/auth/v1/callback
   ```
   Replace `[YOUR_PROJECT_REF]` with your Supabase project reference ID
   (found in: Supabase Dashboard → Settings → General → Reference ID)
8. Click **Create**
9. **Copy** the Client ID and Client Secret

---

## Step 2 — Enable Google in Supabase

1. Open [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **Authentication → Providers**
4. Find **Google** and toggle it **Enabled**
5. Paste your **Client ID** and **Client Secret**
6. Click **Save**

---

## Step 3 — Get Supabase JWT Secret

1. In Supabase Dashboard → **Settings → API**
2. Scroll to **JWT Settings**
3. Copy the **JWT Secret**

---

## Step 4 — Update Your .env

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
OAUTH_REDIRECT_URL=http://localhost:3000/auth/callback
```

For production, change `OAUTH_REDIRECT_URL` to:
```env
OAUTH_REDIRECT_URL=https://your-app.vercel.app/auth/callback
```

---

## API Endpoints (Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/auth/google` | Returns the Google OAuth URL |
| `GET` | `/api/v1/auth/google/redirect` | Directly redirects browser to Google |
| `POST` | `/api/v1/auth/google/verify` | Verifies Supabase token → returns app JWT |
| `GET` | `/api/v1/auth/providers` | Lists configured auth providers |

---

## Frontend Integration (Next.js)

### 1. Initiate Google Login

```tsx
// components/auth/GoogleLoginButton.tsx
const handleGoogleLogin = async () => {
  const res = await fetch('/api/v1/auth/google');
  const { oauth_url } = await res.json();
  window.location.href = oauth_url;   // Redirect to Google
};

return (
  <button onClick={handleGoogleLogin} className="btn-google">
    <GoogleIcon />
    Continue with Google
  </button>
);
```

### 2. Handle the Callback Page

After Google login, Supabase redirects to `/auth/callback` with an `access_token` in the URL hash.

```tsx
// app/auth/callback/page.tsx
'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AuthCallback() {
  const router = useRouter();

  useEffect(() => {
    const hash = window.location.hash;
    const params = new URLSearchParams(hash.replace('#', '?'));
    const accessToken = params.get('access_token');

    if (accessToken) {
      // Exchange Supabase token for our app JWT
      fetch('/api/v1/auth/google/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_token: accessToken }),
      })
        .then(res => res.json())
        .then(data => {
          // Store our app JWT
          localStorage.setItem('truthlens_token', data.access_token);
          localStorage.setItem('truthlens_user', JSON.stringify(data.user));
          router.push('/');    // Redirect to home
        })
        .catch(() => router.push('/login?error=oauth_failed'));
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen">
      <p>Completing sign in...</p>
    </div>
  );
}
```

### 3. Use the Token in API Calls

```tsx
// lib/api.ts
const token = localStorage.getItem('truthlens_token');

const response = await fetch('/api/v1/users/me', {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

---

## User Account Behavior

| Scenario | What Happens |
|----------|-------------|
| First Google login | New account created automatically |
| Google login with existing email | Google account linked to existing account |
| Same Google account, login again | Profile updated (avatar URL refreshed) |
| Email/password user → Google login | Accounts merged by email |

---

## Troubleshooting

**"SUPABASE_JWT_SECRET not configured"**
→ Add `SUPABASE_JWT_SECRET` to your `.env` file

**"Invalid Supabase token"**
→ Token may be expired (Supabase tokens expire in 1 hour) or wrong JWT Secret

**Redirect URI mismatch**
→ The redirect URI in Google Cloud Console must exactly match the one in Supabase

**User created but not appearing in our DB**
→ Check `/api/v1/auth/providers` to verify Google is configured
→ Check server logs for the `/api/v1/auth/google/verify` call
