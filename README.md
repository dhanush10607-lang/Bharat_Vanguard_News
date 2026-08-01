# TruthLens AI

> **An AI-powered news intelligence platform** that collects news from trusted sources, analyzes it, groups related reports, scores transparency, and presents searchable insights.

[![Status](https://img.shields.io/badge/status-active%20development-blue)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-yellow)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)

---

## 🎯 Mission

Collect news from multiple trusted sources, analyze it with AI, verify it through evidence, and present users with **transparent, searchable information** — not just headlines.

---

## 🏗️ Architecture

```
Users → Vercel (Next.js) → Render (FastAPI) → Supabase (PostgreSQL)
                                             → Upstash (Redis)
                                             → Bonsai (Elasticsearch)
Render Cron → RSS/API Collectors → NLP Pipeline → DB
```

**Total infrastructure cost: $0/month** (all free tiers)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- A [Supabase](https://supabase.com) free account
- A [Upstash](https://upstash.com) free Redis instance

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/truthlens-ai.git
cd truthlens-ai

# Copy and fill in environment variables
cp .env.example .env
# Edit .env with your Supabase, Redis, and API keys
```

### 2. Install Dependencies

```bash
# Backend API
pip install -r requirements.txt

# NLP Worker (heavy - only if running locally)
pip install -r requirements-nlp.txt
python -m spacy download en_core_web_sm
```

### 3. Setup Supabase Database

1. Open [Supabase Dashboard](https://app.supabase.com)
2. Go to **SQL Editor**
3. Run the contents of `docs/supabase_setup.sql` (enables extensions)
4. Then run migrations:

```bash
alembic upgrade head
```

### 4. Start Data Collection

```bash
# Run RSS collector once to populate initial articles
python services/collector/rss_collector.py
```

### 5. Start the API Server

```bash
uvicorn apps.api.main:app --reload --port 8000
# Visit: http://localhost:8000/docs
```

### 6. Start the Frontend

```bash
cd apps/frontend
npm install
npm run dev
# Visit: http://localhost:3000
```

---

## 📁 Project Structure

```
truthlens-ai/
├── apps/
│   ├── frontend/          # Next.js 14 (App Router + TypeScript)
│   └── api/               # FastAPI Backend
│
├── services/
│   ├── collector/         # RSS + API data collectors
│   ├── parser/            # HTML content extraction
│   ├── nlp/               # NLP pipeline (NER, topics, sentiment)
│   ├── deduplication/     # Event clustering
│   ├── summarizer/        # AI summarization
│   └── verification/      # Trust scoring
│
├── shared/
│   ├── models/            # SQLAlchemy DB models
│   ├── utils/             # Shared utilities
│   ├── config.py          # App configuration
│   └── database.py        # DB connection
│
├── migrations/            # Alembic migrations
├── docs/                  # Documentation
└── tests/                 # Test suite
```

---

## 🗺️ Roadmap

| Stage | Status | Description |
|-------|--------|-------------|
| 0 | ✅ Done | Repository scaffold, DB schema, config |
| 1 | 🔄 Next | Supabase setup + Alembic migrations |
| 2 | ⏳ Planned | RSS collector (25 feeds) live |
| 3 | ⏳ Planned | FastAPI backend deployed on Render |
| 4 | ⏳ Planned | Next.js frontend deployed on Vercel |
| 5 | ⏳ Planned | NLP pipeline (NER, topics, sentiment) |
| 6 | ⏳ Planned | Deduplication + event clustering |
| 7 | ⏳ Planned | AI summarization (BART) |
| 8 | ⏳ Planned | Trust/transparency scoring |
| 9 | ⏳ Planned | Analytics dashboard |
| 10+ | ⏳ Future | AI assistant, semantic search, recommendations |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/articles` | List articles with filters |
| GET | `/api/v1/articles/{slug}` | Get article detail |
| GET | `/api/v1/events` | List events (grouped stories) |
| GET | `/api/v1/events/trending` | Trending events |
| GET | `/api/v1/search?q=query` | Full-text search |
| GET | `/api/v1/analytics/summary` | Platform statistics |
| GET | `/api/v1/publishers` | List publishers |
| POST | `/api/v1/users/register` | Create account |
| POST | `/api/v1/users/login` | Login |
| GET | `/health` | Health check |

Full docs: `http://localhost:8000/docs` (Swagger UI)

---

## 📰 News Sources (25 RSS Feeds)

| Publisher | Country | Categories |
|-----------|---------|------------|
| BBC News | 🇬🇧 UK | World, Tech, Business, Science, Health |
| TechCrunch | 🇺🇸 US | Technology, AI, Startups |
| The Verge | 🇺🇸 US | Technology, AI |
| Ars Technica | 🇺🇸 US | Technology, Science |
| MIT Tech Review | 🇺🇸 US | AI, Technology |
| Wired | 🇺🇸 US | Technology |
| The Hindu | 🇮🇳 India | India, World, Business, Science |
| NDTV | 🇮🇳 India | India |
| Hindustan Times | 🇮🇳 India | India |
| Al Jazeera | 🌍 Global | World |
| NASA | 🇺🇸 US | Science |
| WHO | 🌍 Global | Health |
| Reuters (via GNews) | 🌍 Global | World, Business |
| AP News (via GNews) | 🇺🇸 US | World |
| Nature | 🌍 Global | Science |
| ScienceDaily | 🌍 Global | Science |
| Hacker News | 🌍 Global | Technology |
| + Guardian API | 🇬🇧 UK | World, Tech, Science, Business |

---

## 🤖 AI Models (All Free, No API Cost)

| Task | Model |
|------|-------|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| NER | `spaCy en_core_web_sm` |
| Topic Classification | `facebook/bart-large-mnli` (zero-shot) |
| Sentiment | `cardiffnlp/twitter-roberta-base-sentiment-latest` |
| Summarization | `facebook/bart-large-cnn` |
| Keywords | `KeyBERT` |

---

## 🔒 Privacy & Ethics

- **No content scraping without permission** — Only RSS feeds, APIs with ToS permission, and public data
- **No fact-checking claims** — Trust scores are "evidence strength" indicators, not verdicts
- **Source transparency** — Every summary links back to original source articles
- **User data** — Minimal collection; no selling or sharing

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with: FastAPI, Next.js, Supabase, HuggingFace Transformers, spaCy, Sentence Transformers, SQLAlchemy, Alembic, trafilatura.
