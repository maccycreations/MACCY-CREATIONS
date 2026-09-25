# MACCY-CREATIONS

Supabase integration has been added for project `kyrsdewrgqejoajhpfrn`.

## Configuration

```bash
cp .env.example .env
# Edit .env and replace <YOUR-PASSWORD> in DATABASE_URL locally.
```

The publishable Supabase key is included in `.env.example`; `.env` is intentionally not committed. Never put a database password or a Supabase service-role key in source control.

## Supabase CLI

Install the Supabase CLI, then run locally from this repository:

```bash
supabase login
supabase link --project-ref kyrsdewrgqejoajhpfrn
supabase db push
```

The migration in `supabase/migrations/0001_initial.sql` creates:

- `profiles`
- `user_settings`
- `app_data`
- Auth user provisioning trigger
- Owner-only RLS policies based on `auth.uid()`

## Python client

Install the dependencies used by `supabase_client.py`:

```bash
pip install supabase python-dotenv
```

Example:

```python
from supabase_client import get_supabase

client = get_supabase()
response = client.auth.sign_up({"email": "user@example.com", "password": "use-a-strong-password"})
```

The repository currently contains no application entrypoint to wire into this client, so this commit provides the secure Supabase foundation rather than claiming the entire application is already connected. The supplied Postgres URI contained a password placeholder; direct Postgres operations cannot work until `DATABASE_URL` is filled locally.
