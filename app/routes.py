from __future__ import annotations

from typing import Any, Callable, Dict, List, Type, TypeVar

from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel, select

from app.database import engine
from app.models import AIConfig, Application, CareerTrack, JobListing, Resume, Roadmap, Skill, UserProfile
from app.schemas import (
    AIConfigCreate,
    ApplicationCreate,
    CareerTrackCreate,
    JobCreate,
    ResumeCreate,
    RoadmapCreate,
    SkillCreate,
    UserProfileCreate,
)
from sqlmodel import Session

router = APIRouter(prefix="/api/local", tags=["local-career-hub"])

T = TypeVar("T", bound=SQLModel)


def serialize(value: SQLModel) -> Dict[str, Any]:
    return value.model_dump() if hasattr(value, "model_dump") else value.dict()


def collection(model: Type[T]) -> List[Dict[str, Any]]:
    with Session(engine) as session:
        return [serialize(item) for item in session.exec(select(model)).all()]


def create_record(model: Type[T], payload: SQLModel) -> Dict[str, Any]:
    with Session(engine) as session:
        record = model(**serialize(payload))
        session.add(record)
        session.commit()
        session.refresh(record)
        return serialize(record)


@router.get("/dashboard")
def dashboard() -> Dict[str, Any]:
    with Session(engine) as session:
        skills = session.exec(select(Skill)).all()
        jobs = session.exec(select(JobListing)).all()
        applications = session.exec(select(Application)).all()
        roadmaps = session.exec(select(Roadmap)).all()
        resumes = session.exec(select(Resume)).all()
    return {
        "skills": len(skills),
        "jobs": len(jobs),
        "applications": len(applications),
        "roadmaps": len(roadmaps),
        "resumes": len(resumes),
        "top_skills": [item.name for item in skills[:8]],
    }


@router.post("/profiles")
def create_profile(payload: UserProfileCreate):
    return create_record(UserProfile, payload)


@router.get("/profiles")
def profiles():
    return collection(UserProfile)


@router.post("/skills")
def create_skill(payload: SkillCreate):
    return create_record(Skill, payload)


@router.get("/skills")
def skills():
    return collection(Skill)


@router.post("/careers")
def create_career(payload: CareerTrackCreate):
    return create_record(CareerTrack, payload)


@router.get("/careers")
def careers():
    return collection(CareerTrack)


@router.post("/roadmaps")
def create_roadmap(payload: RoadmapCreate):
    data = serialize(payload)
    data["steps"] = data["steps"] if isinstance(data["steps"], str) else "\n".join(data["steps"])
    return create_record(Roadmap, type("RoadmapPayload", (), {"model_dump": lambda self: data})())


@router.get("/roadmaps")
def roadmaps():
    return collection(Roadmap)


@router.post("/resumes")
def create_resume(payload: ResumeCreate):
    return create_record(Resume, payload)


@router.get("/resumes")
def resumes():
    return collection(Resume)


@router.post("/jobs")
def create_job(payload: JobCreate):
    return create_record(JobListing, payload)


@router.get("/jobs")
def jobs():
    return collection(JobListing)


@router.post("/applications")
def create_application(payload: ApplicationCreate):
    return create_record(Application, payload)


@router.get("/applications")
def applications():
    return collection(Application)


@router.post("/ai-config")
def create_ai_config(payload: AIConfigCreate):
    # Store only a hint, never a raw provider secret.
    return create_record(AIConfig, payload)


@router.get("/ai-config")
def ai_configs():
    return collection(AIConfig)
