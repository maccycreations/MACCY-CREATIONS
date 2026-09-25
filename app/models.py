from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str
    target_role: Optional[str] = None
    created_at: str = "2026-01-01T00:00:00Z"


class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    proficiency: str = "Beginner"
    certificate_url: Optional[str] = None
    progress: int = 0
    owner_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")


class CareerTrack(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    level: str
    skills: str
    salary_range: str
    demand: str
    resources: str
    description: Optional[str] = None


class Roadmap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    target_role: str
    steps: str
    owner_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")


class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    career_role: str
    summary: str
    ats_score: int = 0
    file_url: Optional[str] = None
    owner_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")


class JobListing(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company: str
    title: str
    location: str = "Remote"
    remote: bool = True
    salary: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: str = "Public"
    owner_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")


class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company: str
    title: str
    status: str = "Saved"
    date_applied: Optional[str] = None
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None
    job_id: Optional[int] = Field(default=None, foreign_key="joblisting.id")
    owner_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")


class AIConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str
    model_name: str
    api_key_hint: Optional[str] = None
    enabled: bool = True
    owner_id: Optional[int] = Field(default=None, foreign_key="userprofile.id")
