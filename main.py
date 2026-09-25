from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from auth import bearer_token, get_current_user
from supabase_client import database_url, get_supabase, get_user_supabase

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app = FastAPI(title="MACCY-CREATIONS", version="1.0.0")


class SignUpPayload(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    display_name: str | None = None


class LoginPayload(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class ProfilePayload(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=120)
    bio: str | None = None


class AppDataPayload(BaseModel):
    entity_type: str = Field(..., min_length=1, max_length=80)
    payload: Dict[str, Any]


@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "project": "MACCY-CREATIONS"})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, authorization: str | None = Header(default=None)):
    try:
        token = bearer_token(authorization)
    except ValueError:
        return RedirectResponse(url="/login", status_code=307)

    user = get_current_user(token)
    if user is None:
        return RedirectResponse(url="/login", status_code=307)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": {"id": user.id, "email": user.email, "name": (getattr(user, "user_metadata", {}) or {}).get("full_name")},
            "project": "MACCY-CREATIONS",
        },
    )


@app.get("/health")
def health() -> Dict[str, Any]:
    db_value = os.getenv("DATABASE_URL", "")
    return {
        "status": "ok",
        "project": "MACCY-CREATIONS",
        "supabase_url": os.getenv("SUPABASE_URL", ""),
        "database_configured": bool(db_value and "<YOUR-PASSWORD>" not in db_value and "[YOUR-PASSWORD>" not in db_value),
    }


@app.get("/supabase")
def supabase_status() -> Dict[str, Any]:
    try:
        get_supabase()
        return {"status": "configured", "project_ref": "kyrsdewrgqejoajhpfrn", "auth_ready": True}
    except Exception as exc:
        return {"status": "not_configured", "message": str(exc)}


@app.post("/api/auth/signup")
def sign_up(payload: SignUpPayload) -> Dict[str, Any]:
    try:
        response = get_supabase().auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {"data": {"full_name": payload.display_name or payload.email.split("@")[0]}},
        })
        user = getattr(response, "user", None)
        if not user:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {
            "status": "ok",
            "confirmation_required": getattr(response, "session", None) is None,
            "user": {"id": user.id, "email": user.email},
            "access_token": getattr(getattr(response, "session", None), "access_token", None),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Supabase signup failed: {exc}") from exc


@app.post("/api/auth/login")
def login(payload: LoginPayload) -> Dict[str, Any]:
    try:
        response = get_supabase().auth.sign_in_with_password({"email": payload.email, "password": payload.password})
        session = getattr(response, "session", None)
        user = getattr(response, "user", None)
        if session is None or user is None:
            raise HTTPException(status_code=401, detail="Login failed")
        return {
            "status": "ok",
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user": {"id": user.id, "email": user.email},
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {exc}") from exc


@app.get("/api/auth/me")
def auth_me(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    metadata = getattr(user, "user_metadata", {}) or {}
    return {"status": "ok", "user": {"id": user.id, "email": user.email, "name": metadata.get("full_name")}}


@app.post("/api/auth/logout")
def logout(authorization: str | None = Header(default=None)) -> Dict[str, str]:
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    try:
        get_user_supabase(token).auth.sign_out()
    except Exception:
        pass
    return {"status": "ok", "message": "Signed out"}


@app.get("/api/profiles")
def list_profiles(authorization: str | None = Header(default=None)) -> List[Dict[str, Any]]:
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    response = get_user_supabase(token).table("profiles").select("*").eq("id", user.id).execute()
    return response.data or []


@app.put("/api/profiles")
def update_profile(payload: ProfilePayload, authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    response = get_user_supabase(token).table("profiles").upsert({"id": user.id, "display_name": payload.display_name}).execute()
    return (response.data or [{"id": user.id, "display_name": payload.display_name}])[0]


@app.get("/api/app-data")
def list_app_data(entity_type: str | None = None, authorization: str | None = Header(default=None)) -> List[Dict[str, Any]]:
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    query = get_user_supabase(token).table("app_data").select("*").eq("user_id", user.id)
    if entity_type:
        query = query.eq("entity_type", entity_type)
    response = query.order("updated_at", desc=True).execute()
    return response.data or []


@app.post("/api/app-data")
def create_app_data(payload: AppDataPayload, authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    response = get_user_supabase(token).table("app_data").insert({
        "user_id": user.id,
        "entity_type": payload.entity_type,
        "payload": payload.payload,
    }).execute()
    return (response.data or [{"status": "ok"}])[0]


@app.get("/api/dashboard")
def dashboard_summary(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    try:
        token = bearer_token(authorization)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    app_data = list_app_data(authorization=authorization)
    return {
        "status": "ok",
        "user": {"id": user.id, "email": user.email, "name": (getattr(user, "user_metadata", {}) or {}).get("full_name")},
        "counts": {
            "records": len(app_data),
            "projects": len([item for item in app_data if item.get("entity_type") == "project"]),
            "clients": len([item for item in app_data if item.get("entity_type") == "client"]),
            "notes": len([item for item in app_data if item.get("entity_type") == "note"]),
        },
    }


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
