from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from auth import bearer_token, get_current_user
from supabase_client import database_url, get_supabase, get_user_supabase

app = FastAPI(title="MACCY-CREATIONS", version="1.0.0")


class SignUpPayload(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = None


class LoginPayload(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class ProfilePayload(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=120)


class AppDataPayload(BaseModel):
    entity_type: str = Field(..., min_length=1, max_length=80)
    payload: Dict[str, Any]


def current_user(authorization: Optional[str]):
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return token, user


@app.get("/health")
def health() -> Dict[str, Any]:
    database_value = os.getenv("DATABASE_URL", "")
    return {"status": "ok", "project": "MACCY-CREATIONS", "supabase_url": os.getenv("SUPABASE_URL", ""), "database_configured": bool(database_value and "<YOUR-PASSWORD>" not in database_value and "[YOUR-PASSWORD]" not in database_value)}


@app.get("/supabase")
def supabase_status() -> Dict[str, Any]:
    try:
        get_supabase()
        return {"status": "configured", "url": os.getenv("SUPABASE_URL", ""), "project_ref": "kyrsdewrgqejoajhpfrn", "auth_ready": True}
    except Exception as exc:
        return {"status": "not_configured", "message": str(exc)}


@app.post("/auth/signup")
def sign_up(payload: SignUpPayload) -> Dict[str, Any]:
    try:
        response = get_supabase().auth.sign_up({"email": payload.email, "password": payload.password, "options": {"data": {"full_name": payload.display_name or payload.email.split("@")[0]}}})
        user = getattr(response, "user", None)
        if user is None:
            raise HTTPException(status_code=400, detail="Signup failed")
        session = getattr(response, "session", None)
        return {"status": "ok", "confirmation_required": session is None, "user": {"id": user.id, "email": user.email}, "access_token": getattr(session, "access_token", None) if session else None, "refresh_token": getattr(session, "refresh_token", None) if session else None}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Supabase signup failed: {exc}") from exc


@app.post("/auth/login")
def login(payload: LoginPayload) -> Dict[str, Any]:
    try:
        response = get_supabase().auth.sign_in_with_password({"email": payload.email, "password": payload.password})
        session, user = getattr(response, "session", None), getattr(response, "user", None)
        if session is None or user is None:
            raise HTTPException(status_code=401, detail="Login failed")
        return {"status": "ok", "access_token": session.access_token, "refresh_token": session.refresh_token, "user": {"id": user.id, "email": user.email}}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid credentials") from exc


@app.get("/auth/me")
def auth_me(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    _, user = current_user(authorization)
    metadata = getattr(user, "user_metadata", {}) or {}
    return {"status": "ok", "user": {"id": user.id, "email": user.email, "name": metadata.get("full_name")}}


@app.post("/auth/logout")
def logout(authorization: Optional[str] = Header(default=None)) -> Dict[str, str]:
    token, _ = current_user(authorization)
    try:
        get_user_supabase(token).auth.sign_out()
    except Exception:
        pass
    return {"status": "ok", "message": "Signed out locally; discard the client tokens"}


@app.get("/profiles")
def list_profiles(authorization: Optional[str] = Header(default=None)) -> List[Dict[str, Any]]:
    token, user = current_user(authorization)
    response = get_user_supabase(token).table("profiles").select("*").eq("id", user.id).execute()
    return response.data or []


@app.put("/profiles")
def update_profile(payload: ProfilePayload, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    token, user = current_user(authorization)
    response = get_user_supabase(token).table("profiles").upsert({"id": user.id, "display_name": payload.display_name}).execute()
    return (response.data or [{"id": user.id, "display_name": payload.display_name}])[0]


@app.get("/app-data")
def list_app_data(entity_type: Optional[str] = None, authorization: Optional[str] = Header(default=None)) -> List[Dict[str, Any]]:
    token, user = current_user(authorization)
    query = get_user_supabase(token).table("app_data").select("*").eq("user_id", user.id)
    if entity_type:
        query = query.eq("entity_type", entity_type)
    response = query.order("updated_at", desc=True).execute()
    return response.data or []


@app.post("/app-data")
def create_app_data(payload: AppDataPayload, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    token, user = current_user(authorization)
    response = get_user_supabase(token).table("app_data").insert({"user_id": user.id, "entity_type": payload.entity_type, "payload": payload.payload}).execute()
    return (response.data or [{"status": "ok"}])[0]


@app.get("/database")
def database_status() -> Dict[str, Any]:
    try:
        database_url()
        return {"status": "configured"}
    except Exception as exc:
        return {"status": "not_configured", "message": str(exc)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
