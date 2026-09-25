from __future__ import annotations

from typing import Any, Optional

from supabase_client import get_user_supabase


def bearer_token(value: Optional[str]) -> str:
    if not value or not value.startswith("Bearer "):
        raise ValueError("Bearer token required")
    token = value.split(" ", 1)[1].strip()
    if not token:
        raise ValueError("Bearer token required")
    return token


def get_current_user(token: str) -> Optional[Any]:
    try:
        response = get_user_supabase(token).auth.get_user(token)
        return getattr(response, "user", None)
    except Exception:
        return None
