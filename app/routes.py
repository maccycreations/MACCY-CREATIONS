from __future__ import annotations

from typing import Any, Dict, List, Type, TypeVar

from fastapi import APIRouter
from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import AIConfig, Application, CareerTrack, JobListing, Resume, Roadmap, Skill, UserProfile
from app.schemas import AIConfigCreate, ApplicationCreate, CareerTrackCreate, JobCreate, ResumeCreate, RoadmapCreate, SkillCreate, UserProfileCreate

router = APIRouter(prefix="/api/local", tags=["local-career-hub"])
T = TypeVar("T", bound=SQLModel)


def dump(value: Any) -> Dict[str, Any]:
    return value.model_dump() if hasattr(value, "model_dump") else value.dict()


def records(model: Type[T]) -> List[Dict[str, Any]]:
    with Session(engine) as session:
        return [dump(row) for row in session.exec(select(model)).all()]


def create(model: Type[T], payload: Any) -> Dict[str, Any]:
    with Session(engine) as session:
        row = model(**dump(payload))
        session.add(row)
        session.commit()
        session.refresh(row)
        return dump(row)


@router.get("/dashboard")
def dashboard():
    return {"skills": len(records(Skill)), "jobs": len(records(JobListing)), "applications": len(records(Application)), "roadmaps": len(records(Roadmap)), "resumes": len(records(Resume))}


@router.post("/profiles")
def create_profile(payload: UserProfileCreate): return create(UserProfile, payload)
@router.get("/profiles")
def list_profiles(): return records(UserProfile)
@router.post("/skills")
def create_skill(payload: SkillCreate): return create(Skill, payload)
@router.get("/skills")
def list_skills(): return records(Skill)
@router.post("/careers")
def create_career(payload: CareerTrackCreate): return create(CareerTrack, payload)
@router.get("/careers")
def list_careers(): return records(CareerTrack)
@router.post("/roadmaps")
def create_roadmap(payload: RoadmapCreate):
    data = dump(payload)
    data["steps"] = data["steps"] if isinstance(data["steps"], str) else "\n".join(data["steps"])
    return create(Roadmap, type("Payload", (), {"dict": lambda self: data})())
@router.get("/roadmaps")
def list_roadmaps(): return records(Roadmap)
@router.post("/resumes")
def create_resume(payload: ResumeCreate): return create(Resume, payload)
@router.get("/resumes")
def list_resumes(): return records(Resume)
@router.post("/jobs")
def create_job(payload: JobCreate): return create(JobListing, payload)
@router.get("/jobs")
def list_jobs(): return records(JobListing)
@router.post("/applications")
def create_application(payload: ApplicationCreate): return create(Application, payload)
@router.get("/applications")
def list_applications(): return records(Application)
@router.post("/ai-config")
def create_ai_config(payload: AIConfigCreate): return create(AIConfig, payload)
@router.get("/ai-config")
def list_ai_configs(): return records(AIConfig)
