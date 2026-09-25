# MACCY-CREATIONS

A complete, deployable FastAPI starter for the MACCY-CREATIONS brand, backed by Supabase auth and data storage and designed to run locally with a secure environment file.

## Features

- Landing page and login page
- Supabase-based auth (signup, login, logout, current user)
- Protected profile API and app-data API
- Dashboard summary endpoint
- Local health and configuration checks
- Database and RLS-ready schema scripts
- Demo-friendly local startup without a live Supabase connection

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add the real DATABASE_URL password locally before direct Postgres access.
uvicorn main:app --reload
```

Then open:

- http://localhost:8000/
- http://localhost:8000/login
- http://localhost:8000/dashboard

## Environment file

```env
SUPABASE_URL=https://kyrsdewrgqejoajhpfrn.supabase.co
SUPABASE_KEY=sb_publishable_cAtn2dFn4QIv7BSCl7Vmmg_hmOz3jVd
DATABASE_URL=postgresql://postgres:<YOUR-PASSWORD>@db.kyrsdewrgqejoajhpfrn.supabase.co:5432/postgres
```

Do not commit `.env` or service-role keys. Use the publishable key for RLS-backed client access.

## Supabase setup

```bash
supabase login
supabase link --project-ref kyrsdewrgqejoajhpfrn
supabase db push
```

The migration files live in `supabase/migrations/`.

## API examples

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass12345","display_name":"User"}'
```

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass12345"}'
```

Send the access token as:

```text
Authorization: Bearer <access_token>
```
