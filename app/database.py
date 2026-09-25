from __future__ import annotations

from pathlib import Path

from sqlmodel import SQLModel, create_engine, Session

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "career_app.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
    from app.models import Skill, CareerTrack, Roadmap, Resume, JobListing, Application, AIConfig, UserProfile

    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
