from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class UserProfileCreate(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    target_role: Optional[str] = None


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    proficiency: str = "Beginner"
    progress: int = Field(default=0, ge=0, le=100)
    certificate_url: Optional[str] = None


class CareerTrackCreate(BaseModel):
    title: str
    level: str
    skills: str
    salary_range: str
    demand: str
    resources: str
    description: Optional[str] = None


class RoadmapCreate(BaseModel):
    title: str
    target_role: str
    steps: list[str] | str


class ResumeCreate(BaseModel):
    title: str
    career_role: str
    summary: str
    ats_score: int = Field(default=0, ge=0, le=100)
    file_url: Optional[str] = None


class JobCreate(BaseModel):
    company: str
    title: str
    location: str = "Remote"
    remote: bool = True
    salary: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: str = "Public"


class ApplicationCreate(BaseModel):
    company: str
    title: str
    status: str = "Saved"
    date_applied: Optional[str] = None
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None
    job_id: Optional[int] = None


class AIConfigCreate(BaseModel):
    provider: str
    model_name: str
    api_key_hint: Optional[str] = None
    enabled: bool = True
