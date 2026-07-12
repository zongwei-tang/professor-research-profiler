# Professor Research Profiler

A tool for prospective PhD applicants to evaluate potential supervisors. Enter a professor's
name and your research interests; it pulls their publication record from
[Semantic Scholar](https://www.semanticscholar.org/) and uses an LLM to assess the fit.

## Architecture

- **Frontend:** React + TypeScript, Tailwind CSS, Recharts, TanStack Query. Talks to the
  backend over a REST API.
- **Backend:** FastAPI, with a `core`/`crud`/`models`/`schemas`/`services`/`api` layered
  structure. Business logic (Semantic Scholar fetching, multi-provider LLM routing) lives in
  `services/`.
- **Database:** [Turso](https://turso.tech/) (libSQL) via SQLAlchemy ORM, migrated with Alembic.
- **Cache:** Redis, cache-aside with TTL, for professor search/paper results and per-user
  history lists.
- **Auth:** JWT-based signup/login (bcrypt password hashing). All per-user endpoints derive
  the user's identity from the verified token, not from client-supplied input.

## Features

- Search a professor and pick the right person from the candidate list.
- Builds a quick profile: top-cited papers, output by year, and frequent collaborators.
- LLM analysis of their research direction, how their focus shifted, overlaps with your
  interests, and whether to reach out.
- Choose your provider: Anthropic, OpenAI, DeepSeek, or Gemini.
- Per-user history: past analyses are saved and browsable, scoped to your account.

## Running locally

**Backend** (requires [uv](https://docs.astral.sh/uv/)):

```bash
cd backend
uv sync
cp .env.example .env              # fill in API keys, Turso URL/token, JWT_SECRET_KEY
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` requests to the backend at `http://127.0.0.1:8000`.

You'll need a Semantic Scholar key, a Turso database URL and token, a JWT secret
(`python -c "import secrets; print(secrets.token_hex(32))"`), a running Redis instance, and
the key for whichever LLM provider(s) you use.
