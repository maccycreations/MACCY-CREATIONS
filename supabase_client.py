"""Supabase client configuration for MACCY-CREATIONS.

Only the publishable key belongs in application configuration. A Postgres password
must be supplied through the environment and must never be committed.
"""
import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "https://kyrsdewrgqejoajhpfrn.supabase.co")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    if not key:
        raise RuntimeError("SUPABASE_KEY or SUPABASE_PUBLISHABLE_KEY is required")
    return create_client(url, key)


def database_url() -> str:
    value = os.getenv("DATABASE_URL", "")
    if not value or "<YOUR-PASSWORD>" in value or "[YOUR-PASSWORD]" in value:
        raise RuntimeError("Set DATABASE_URL with the Supabase database password before using direct Postgres access")
    return value
