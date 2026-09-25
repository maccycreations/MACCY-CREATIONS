from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from auth import get_current_user
from supabase_client import database_url, get_supabase

app = FastAPI(title="MACCY-CREATIONS", version="1.0.0")


class SignUpPayload(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = None


class LoginPayload(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class ProfilePayload(BaseModel):
    display_name: str
    bio: Optional[str] = None


class AppDataPayload(BaseModel):
    entity_type: str
    payload: Dict[str, Any]


@app.get("/health")
def health() -> Dict[str, Any]:
    database_value = os.getenv("DATABASE_URL", "")
    return {
        "status": "ok",
        "project": "MACCY-CREATIONS",
        "supabase_url": os.getenv("SUPABASE_URL", ""),
        "database_configured": bool(database_value and "<YOUR-PASSWORD>" not in database_value and "[YOUR-PASSWORD]" not in database_value),
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


@app.post("/auth/signup")
def sign_up(payload: SignUpPayload) -> Dict[str, Any]:
    try:
        client = get_supabase()
        response = client.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {
                "data": {
                    "full_name": payload.display_name or payload.email.split('@')[0],
                }
            },
        })
        if hasattr(response, "user") and response.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {
            "status": "signup_initiated",
            "user": getattr(response, "user", None),
            "session": getattr(response, "session", None),
        }
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=400, detail=f"Supabase signup failed: {exc}") from exc


@app.post("/auth/login")
def login(payload: LoginPayload) -> Dict[str, Any]:
    try:
        client = get_supabase()
        response = client.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
        session = getattr(response, "session", None)
        user = getattr(response, "user", None)
        if session is None or user is None:
            raise HTTPException(status_code=401, detail="Login failed")
        return {
            "status": "ok",
            "access_token": getattr(session, "access_token", None),
            "refresh_token": getattr(session, "refresh_token", None),
            "user": {
                "id": getattr(user, "id", None),
                "email": getattr(user, "email", None),
            },
        }
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {exc}") from exc


@app.get("/auth/me")
def auth_me(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization.split(" ", 1)[1]
    user = get_current_user(token)
    return {
        "status": "ok",
        "user": {
            "id": getattr(user, "id", None),
            "email": getattr(user, "email", None),
            "name": getattr(user, "user_metadata", {}).get("full_name") if hasattr(user, "user_metadata") else None,
        },
    }


@app.post("/auth/logout")
def logout() -> Dict[str, str]:
    try:
        client = get_supabase()
        client.auth.sign_out()
        return {"status": "ok", "message": "Signed out"}
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=400, detail=f"Logout failed: {exc}") from exc


@app.get("/profiles")
def list_profiles(authorization: Optional[str] = Header(default=None)) -> List[Dict[str, Any]]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization.split(" ", 1)[1]
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        client = get_supabase()
        response = client.table("profiles").select("*").eq("id", user.id).execute()
        return response.data if hasattr(response, "data") else []
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=503, detail=f"Supabase is not configured: {exc}") from exc


@app.post("/profiles")
def create_profile(payload: ProfilePayload, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization.split(" ", 1)[1]
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        client = get_supabase()
        profile = client.table("profiles").upsert({
            "id": user.id,
            "display_name": payload.display_name,
        }).execute()
        return profile.data[0] if hasattr(profile, "data") and profile.data else {"status": "ok"}
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=503, detail=f"Supabase profile write failed: {exc}") from exc


@app.get("/app-data")
def list_app_data(authorization: Optional[str] = Header(default=None)) -> List[Dict[str, Any]]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization.split(" ", 1)[1]
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        client = get_supabase()
        response = client.table("app_data").select("*").eq("user_id", user.id).execute()
        return response.data if hasattr(response, "data") else []
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=503, detail=f"Supabase app-data query failed: {exc}") from exc


@app.post("/app-data")
def create_app_data(payload: AppDataPayload, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization.split(" ", 1)[1]
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        client = get_supabase()
        response = client.table("app_data").insert({
            "user_id": user.id,
            "entity_type": payload.entity_type,
            "payload": payload.payload,
        }).execute()
        return response.data[0] if hasattr(response, "data") and response.data else {"status": "ok"}
    except Exception as exc:  # pragma: no cover - configuration guard
        raise HTTPException(status_code=503, detail=f"Supabase app-data write failed: {exc}") from exc


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
