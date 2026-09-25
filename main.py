from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.database import init_db
from app.routes import router as local_router
from app.seed import seed_database
from auth import bearer_token, get_current_user
from supabase_client import database_url, get_supabase, get_user_supabase

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="MACCY-CREATIONS Career Hub", version="1.1.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.include_router(local_router)


class SignUpPayload(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = None


class LoginPayload(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class ProfilePayload(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=120)
    bio: Optional[str] = None


class AppDataPayload(BaseModel):
    entity_type: str = Field(..., min_length=1, max_length=80)
    payload: Dict[str, Any]


@app.on_event("startup")
def startup() -> None:
    init_db()
    seed_database()


@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "project": "MACCY-CREATIONS"})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "project": "MACCY-CREATIONS"})


@app.get("/health")
def health():
    value = os.getenv("DATABASE_URL", "")
    return {"status": "ok", "project": "MACCY-CREATIONS", "supabase_url": os.getenv("SUPABASE_URL", ""), "database_configured": bool(value and "<YOUR-PASSWORD>" not in value and "[YOUR-PASSWORD]" not in value)}


@app.get("/supabase")
def supabase_status():
    try:
        get_supabase()
        return {"status": "configured", "project_ref": "kyrsdewrgqejoajhpfrn", "auth_ready": True}
    except Exception as exc:
        return {"status": "not_configured", "message": str(exc)}


def authenticated_user(authorization: Optional[str]):
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return token, user


@app.post("/api/auth/signup")
def sign_up(payload: SignUpPayload):
    try:
        response = get_supabase().auth.sign_up({"email": payload.email, "password": payload.password, "options": {"data": {"full_name": payload.display_name or payload.email.split("@")[0]}}})
        user, session = getattr(response, "user", None), getattr(response, "session", None)
        if not user: raise HTTPException(status_code=400, detail="Signup failed")
        return {"status": "ok", "confirmation_required": session is None, "user": {"id": user.id, "email": user.email}, "access_token": getattr(session, "access_token", None) if session else None, "refresh_token": getattr(session, "refresh_token", None) if session else None}
    except HTTPException: raise
    except Exception as exc: raise HTTPException(status_code=400, detail=f"Supabase signup failed: {exc}") from exc


@app.post("/api/auth/login")
def login(payload: LoginPayload):
    try:
        response = get_supabase().auth.sign_in_with_password({"email": payload.email, "password": payload.password})
        session, user = getattr(response, "session", None), getattr(response, "user", None)
        if not session or not user: raise HTTPException(status_code=401, detail="Login failed")
        return {"status": "ok", "access_token": session.access_token, "refresh_token": session.refresh_token, "user": {"id": user.id, "email": user.email}}
    except HTTPException: raise
    except Exception as exc: raise HTTPException(status_code=401, detail="Invalid credentials") from exc


@app.get("/api/auth/me")
def auth_me(authorization: Optional[str] = Header(default=None)):
    _, user = authenticated_user(authorization)
    metadata = getattr(user, "user_metadata", {}) or {}
    return {"status": "ok", "user": {"id": user.id, "email": user.email, "name": metadata.get("full_name")}}


@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(default=None)):
    token, _ = authenticated_user(authorization)
    try: get_user_supabase(token).auth.sign_out()
    except Exception: pass
    return {"status": "ok", "message": "Signed out"}


@app.get("/api/profiles")
def list_profiles(authorization: Optional[str] = Header(default=None)):
    token, user = authenticated_user(authorization)
    return get_user_supabase(token).table("profiles").select("*").eq("id", user.id).execute().data or []


@app.put("/api/profiles")
def update_profile(payload: ProfilePayload, authorization: Optional[str] = Header(default=None)):
    token, user = authenticated_user(authorization)
    response = get_user_supabase(token).table("profiles").upsert({"id": user.id, "display_name": payload.display_name}).execute()
    return (response.data or [{"id": user.id, "display_name": payload.display_name}])[0]


@app.get("/api/app-data")
def list_app_data(entity_type: Optional[str] = None, authorization: Optional[str] = Header(default=None)):
    token, user = authenticated_user(authorization)
    query = get_user_supabase(token).table("app_data").select("*").eq("user_id", user.id)
    if entity_type: query = query.eq("entity_type", entity_type)
    return query.order("updated_at", desc=True).execute().data or []


@app.post("/api/app-data")
def create_app_data(payload: AppDataPayload, authorization: Optional[str] = Header(default=None)):
    token, user = authenticated_user(authorization)
    response = get_user_supabase(token).table("app_data").insert({"user_id": user.id, "entity_type": payload.entity_type, "payload": payload.payload}).execute()
    return (response.data or [{"status": "ok"}])[0]


@app.get("/database")
def database_status():
    try:
        database_url(); return {"status": "configured"}
    except Exception as exc: return {"status": "not_configured", "message": str(exc)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
