# Bharat Vanguard News (BVN) — Deployment Guide

## Architecture Overview

```
[Render Free] FastAPI API ─────────────────────────────► [Supabase]
[Render Cron] RSS Collector (every 15min) ──────────────► PostgreSQL + pgvector
[Render Cron] Guardian Collector (every 6h) ────────────► Auth + Storage
[Render Cron] NLP Worker (every 30min) ─────────────────►
[Vercel Free] Next.js Frontend ─────────────────────────► [Render API]
```

---

## Step 1 — Supabase Setup

1. Go to [supabase.com](https://supabase.com) → New project
2. Note your **Project URL**, **Anon Key**, **Service Role Key**, **JWT Secret**
3. In the SQL editor, run the `docs/supabase_setup.sql` file to:
   - Enable `pgvector` extension
   - Create all tables
   - Set up Row Level Security
4. Go to **Authentication → Providers → Google** and enable it
   - Add your Google OAuth client credentials (see `docs/google_oauth_setup.md`)

---

## Step 2 — Backend Deployment (Render)

### Option A: Blueprint (Recommended)
1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your GitHub repo
4. Render reads `render.yaml` and creates all services automatically

### Option B: Manual
1. New → Web Service → Connect GitHub
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`
4. Set all environment variables from `.env.example`

### Required Environment Variables
```
DATABASE_URL=postgresql+asyncpg://...  (from Supabase)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
JWT_SECRET_KEY=any-random-secure-string
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app.vercel.app
GUARDIAN_API_KEY=your-guardian-key  (optional, free at theguardian.com/open-platform)
```

### Keep-Alive (Prevent Render Sleep)
Render free tier sleeps after 15 minutes of inactivity.
1. Sign up for [uptimerobot.com](https://uptimerobot.com) (free)
2. New Monitor → HTTP(S) → URL: `https://your-api.onrender.com/health`
3. Set interval: **5 minutes**

---

## Step 3 — Frontend Deployment (Vercel)

1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo
3. **Framework**: Next.js (auto-detected)
4. **Root Directory**: `apps/frontend`
5. Set environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-api.onrender.com
   ```
6. Deploy ✓

---

## Step 4 — GitHub Actions CI/CD

Add these secrets to your GitHub repo (Settings → Secrets):

| Secret | Where to get it |
|---|---|
| `RENDER_API_KEY` | Render Dashboard → Account → API Keys |
| `RENDER_SERVICE_ID` | Render Dashboard → your service → URL contains the ID |

CI runs on every PR, deploys on every push to `main`.

---

## Step 5 — First Run Checklist

```bash
# 1. Run database migrations
make migrate

# 2. Seed publishers
python scripts/seed_publishers.py  # (see docs/supabase_setup.sql)

# 3. Run RSS collector once to populate articles
make collector

# 4. Install NLP deps and run NLP worker
make install-nlp
make nlp

# 5. Start API server locally
make api
# → http://localhost:8000/docs

# 6. Start frontend locally
cd apps/frontend && npm run dev
# → http://localhost:3000
```

---

## Monitoring & Observability

- **Health check**: `GET /health` — returns status, version, uptime
- **API docs**: `GET /docs` — Swagger UI (disable in production if needed)
- **Render logs**: Available in the Render dashboard in real-time
- **Error tracking**: Add `SENTRY_DSN` to env vars and install `sentry-sdk` for error monitoring

---

## Free Tier Limits

| Service | Free Limit | Notes |
|---|---|---|
| Render Web Service | 750 hrs/month, sleeps after 15min | Use UptimeRobot to keep alive |
| Render Cron | 750 hrs/month | NLP worker only runs briefly per batch |
| Supabase | 500MB DB, 1GB storage | Should be plenty for Phase 1 |
| Vercel | 100GB bandwidth/month | More than enough |
| The Guardian API | 500 req/day | ~10,000 articles/month |
