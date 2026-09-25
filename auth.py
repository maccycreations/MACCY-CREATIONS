from __future__ import annotations

from typing import Any, Optional

from supabase_client import get_supabase


def get_current_user(token: str) -> Optional[Any]:
    try:
        client = get_supabase()
        response = client.auth.get_user(token)
        return getattr(response, "user", None)
    except Exception:
        return None
