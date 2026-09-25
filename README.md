# Product completion notes

## New capabilities

- Local sync events now carry a user id and can be pushed through a user's Supabase JWT to the RLS-protected `app_data` table.
- Failed sync events stay queued and increment their attempt count.
- PDF, DOCX, and TXT resume uploads are parsed into text using `pypdf` and `python-docx`.
- ATS analysis runs against extracted resume text.
- Remotive has been added as an additional public job API connector.
- Gemini and Anthropic HTTP adapters have been added alongside OpenAI-compatible and xAI adapters.
- AI completion and sync mutation endpoints require a valid bearer token.

## Run and verify

```bash
pip install -r requirements.txt
uvicorn main:app --reload
pytest
```

Use `POST /api/product/sync/push` with a Supabase access token after applying the Supabase migrations. The `app_data` table must allow the authenticated user to upsert rows under RLS.

Only public APIs and approved integrations should be connected. LinkedIn, Indeed, Naukri, Glassdoor, and similar services must not be scraped without provider authorization.
