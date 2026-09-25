from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from app.database import engine
from app.models import SyncEvent


def enqueue(entity_type: str, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
    with Session(engine) as session:
        event = SyncEvent(entity_type=entity_type, operation=operation, payload=json.dumps(payload))
        session.add(event)
        session.commit()
        session.refresh(event)
        return event.model_dump()


def pending(limit: int = 100) -> list[SyncEvent]:
    with Session(engine) as session:
        return list(session.exec(select(SyncEvent).where(SyncEvent.synced_at.is_(None)).order_by(SyncEvent.id).limit(limit)).all())


def mark_synced(event_id: int) -> None:
    with Session(engine) as session:
        event = session.get(SyncEvent, event_id)
        if event:
            event.synced_at = datetime.now(timezone.utc).isoformat()
            session.add(event)
            session.commit()
