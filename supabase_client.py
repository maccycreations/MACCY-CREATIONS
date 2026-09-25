"""Supabase client factories.

The publishable key is safe for client-side use only with RLS enabled. Database
passwords and service-role keys must remain server-side environment variables.
"""
import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()
DEFAULT_URL = "https://kyrsdewrgqejoajhpfrn.supabase.co"


def _config() -> tuple[str, str]:
    url = os.getenv("SUPABASE_URL", DEFAULT_URL).rstrip("/")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    if not key:
        raise RuntimeError("SUPABASE_KEY or SUPABASE_PUBLISHABLE_KEY is required")
    return url, key


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    return create_client(*_config())


def get_user_supabase(access_token: str) -> Client:
    """Create a request-scoped client whose PostgREST calls carry the user's JWT."""
    client = create_client(*_config())
    client.postgrest.auth(access_token)
    return client


def database_url() -> str:
    value = os.getenv("DATABASE_URL", "")
    if not value or "<YOUR-PASSWORD>" in value or "[YOUR-PASSWORD]" in value:
        raise RuntimeError("Set DATABASE_URL locally before using direct Postgres access")
    return value
