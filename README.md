# MACCY-CREATIONS

## Current product build

The repository now contains a usable local career-platform MVP plus Supabase authentication/data routes:

- SQLite + SQLModel local database
- Seeded skills, careers, roadmap, resume, jobs, applications, and AI configuration
- Local CRUD API under `/api/local/*`
- Supabase auth/profile/app-data API under `/api/*`
- Landing, login, and dashboard pages
- Static CSS mounted at `/static`
- Automated smoke tests

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Open `http://localhost:8000/`. API documentation is available at `http://localhost:8000/docs`.

## Supabase

```bash
supabase login
supabase link --project-ref kyrsdewrgqejoajhpfrn
supabase db push
```

The publishable key belongs in `.env`; never commit the database password or service-role key. Supabase auth routes require a valid bearer access token. Local MVP routes are intentionally separate from remote Supabase routes so offline data remains available when the network is unavailable.

## Local product APIs

- `GET /api/local/dashboard`
- `GET/POST /api/local/profiles`
- `GET/POST /api/local/skills`
- `GET/POST /api/local/careers`
- `GET/POST /api/local/roadmaps`
- `GET/POST /api/local/resumes`
- `GET/POST /api/local/jobs`
- `GET/POST /api/local/applications`
- `GET/POST /api/local/ai-config`

Provider keys are never accepted by the local AI config API; store only a non-secret hint and configure actual secrets in the server environment.
