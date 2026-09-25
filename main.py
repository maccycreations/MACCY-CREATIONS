from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from supabase_client import database_url, get_supabase

app = FastAPI(title="MACCY-CREATIONS", version="1.0.0")


class ProfilePayload(BaseModel):
    display_name: str
    bio: str | None = None


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "project": "MACCY-CREATIONS",
        "supabase_url": os.getenv("SUPABASE_URL", ""),
        "database_configured": bool(os.getenv("DATABASE_URL") and "<YOUR-PASSWORD>" not in os.getenv("DATABASE_URL", "")),
    }


@app.get("/supabase")
def supabase_status() -> Dict[str, Any]:
    try:
        client = get_supabase()
        return {
            "status": "configured",
            "url": os.getenv("SUPABASE_URL", ""),
            "project_ref": "kyrsdewrgqejoajhpfrn",
            "auth_ready": bool(client),
        }
    except Exception as exc:  # pragma: no cover - configuration guard
        return {
            "status": "not_configured",
            "message": str(exc),
        }


@app.get("/profiles")
def list_profiles() -> List[Dict[str, Any]]:
    try:
        client = get_supabase()
        response = client.table("profiles").select("*").execute()
        return response.data if hasattr(response, "data") else []
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=503, detail=f"Supabase is not configured: {exc}") from exc


@app.post("/profiles")
def create_profile(payload: ProfilePayload) -> Dict[str, Any]:
    try:
        client = get_supabase()
        response = client.auth.get_user()
        user = response.user
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication required")

        profile = client.table("profiles").upsert({
            "id": user.id,
            "display_name": payload.display_name,
        }).execute()
        return profile.data[0] if hasattr(profile, "data") and profile.data else {"status": "ok"}
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=503, detail=f"Supabase profile write failed: {exc}") from exc


@app.get("/database")
def database_status() -> Dict[str, Any]:
    try:
        url = database_url()
        return {"status": "configured", "database_url": url}
    except Exception as exc:  # pragma: no cover - configuration guard
        return {"status": "not_configured", "message": str(exc)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
