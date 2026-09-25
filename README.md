# MACCY-CREATIONS

## Configure and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill DATABASE_URL locally if direct Postgres access is needed.
supabase login
supabase link --project-ref kyrsdewrgqejoajhpfrn
supabase db push
uvicorn main:app --reload
```

The API uses the Supabase project `kyrsdewrgqejoajhpfrn`, request-scoped JWT clients, and RLS-backed tables. Never return or commit database passwords, and never use a service-role key in a browser.

## Endpoints

- `GET /health` and `GET /supabase`: safe configuration checks
- `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`, `POST /auth/logout`
- `GET /profiles`, `PUT /profiles`
- `GET /app-data?entity_type=...`, `POST /app-data`
- `GET /database`: reports configuration only and never returns the connection string

Send protected requests with:

```text
Authorization: Bearer <access_token>
```

The Supabase email-confirmation setting may require the user to confirm their email before login. Migrations `0001_initial.sql` and `0002_operational.sql` configure the schema, RLS, auth trigger, indexes, and update timestamps.
