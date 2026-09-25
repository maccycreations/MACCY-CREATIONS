from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "career_app.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


def init_db() -> None:
    from app.models import AIConfig, Application, CareerTrack, JobListing, Resume, Roadmap, Skill, SyncEvent, UserProfile
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
