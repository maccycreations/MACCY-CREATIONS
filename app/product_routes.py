from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from app.models import JobListing
from app.sync import enqueue, pending
from services.ai import complete
from services.ats import analyze_resume
from services.jobs import fetch_jobs

router = APIRouter(prefix="/api/product", tags=["product"])


class ATSRequest(BaseModel):
    resume_text: str = Field(..., min_length=1)
    job_description: str = ""


class AIRequest(BaseModel):
    provider: str = "openai"
    prompt: str = Field(..., min_length=1)
    model: Optional[str] = None


@router.get("/jobs/search")
async def search_jobs(q: str = Query("python"), remote_only: bool = False):
    return [job.model_dump() for job in await fetch_jobs(q, remote_only)]


@router.post("/ats/analyze")
def ats_analyze(payload: ATSRequest):
    return analyze_resume(payload.resume_text, payload.job_description)


@router.post("/resumes/upload")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"}:
        raise HTTPException(status_code=415, detail="Upload PDF, DOCX, or TXT files")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File must be 10 MB or smaller")
    return {"filename": file.filename, "content_type": file.content_type, "size": len(content), "message": "Upload accepted; parse with a configured document worker before ATS analysis."}


@router.post("/ai/complete")
async def ai_complete(payload: AIRequest):
    try:
        return await complete(payload.provider, payload.prompt, payload.model)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AI provider request failed: {exc}") from exc


@router.post("/sync/queue")
def queue_sync(entity_type: str, operation: str, payload: dict[str, Any]):
    return enqueue(entity_type, operation, payload)


@router.get("/sync/pending")
def pending_sync():
    return [event.model_dump() for event in pending()]
