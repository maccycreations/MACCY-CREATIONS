# MACCY-CREATIONS

This repository now includes a working Supabase configuration scaffold and a minimal FastAPI application shell.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your real local values before runtime.
```

Edit `.env` with the secure values:

```env
SUPABASE_URL=https://kyrsdewrgqejoajhpfrn.supabase.co
SUPABASE_KEY=sb_publishable_cAtn2dFn4QIv7BSCl7Vmmg_hmOz3jVd
DATABASE_URL=postgresql://postgres:<YOUR-PASSWORD>@db.kyrsdewrgqejoajhpfrn.supabase.co:5432/postgres
```

The password must not be committed to GitHub. If it contains special characters, URL-encode it.

## Run the app

```bash
uvicorn main:app --reload
```

## Endpoints

- `GET /health`
- `GET /supabase`
- `GET /profiles`
- `POST /profiles`
- `GET /database`

## Supabase

Run the CLI locally:

```bash
supabase login
supabase link --project-ref kyrsdewrgqejoajhpfrn
supabase db push
```

The RLS setup lives in `supabase/migrations/0001_initial.sql`.
