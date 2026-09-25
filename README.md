# MACCY-CREATIONS

The repository now includes a FastAPI backend with Supabase-ready auth and app-data endpoints. This is the next stage beyond the configuration scaffold.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set the real local password in DATABASE_URL before direct DB access.
uvicorn main:app --reload
```

## Auth endpoints

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`

## User data endpoints

- `GET /profiles`
- `POST /profiles`
- `GET /app-data`
- `POST /app-data`

## Notes

- Use a Bearer token from `/auth/login` on protected endpoints.
- The project is still a backend foundation; the full product UI and domain logic remain to be layered on top of this structure.
