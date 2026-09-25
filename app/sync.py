from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlmodel import Session, select

from app.database import engine
from app.models import SyncEvent
from supabase_client import get_user_supabase


def enqueue(entity_type: str, operation: str, payload: dict[str, Any], user_id: Optional[str] = None) -> dict[str, Any]:
    with Session(engine) as session:
        event = SyncEvent(user_id=user_id, entity_type=entity_type, operation=operation, payload=json.dumps(payload))
        session.add(event)
        session.commit()
        session.refresh(event)
        return event.model_dump()


def pending(user_id: Optional[str] = None, limit: int = 100) -> list[SyncEvent]:
    with Session(engine) as session:
        query = select(SyncEvent).where(SyncEvent.synced_at.is_(None)).order_by(SyncEvent.id).limit(limit)
        if user_id:
            query = query.where(SyncEvent.user_id == user_id)
        return list(session.exec(query).all())


def mark_synced(event_id: int) -> None:
    with Session(engine) as session:
        event = session.get(SyncEvent, event_id)
        if event:
            event.synced_at = datetime.now(timezone.utc).isoformat()
            session.add(event)
            session.commit()


async def push_pending(access_token: str, user_id: str, limit: int = 100) -> dict[str, Any]:
    """Push local mutations through the user's RLS-scoped Supabase JWT.

    Each mutation is written to app_data with a deterministic local event id. A
    failed event stays queued and its attempt counter is incremented.
    """
    client = get_user_supabase(access_token)
    events = pending(user_id, limit)
    pushed = 0
    failed = 0
    for event in events:
        try:
            payload = json.loads(event.payload)
            row = {
                "id": f"local-{event.id}",
                "user_id": user_id,
                "entity_type": event.entity_type,
                "payload": {"operation": event.operation, "data": payload, "client_updated_at": event.created_at},
            }
            client.table("app_data").upsert(row, on_conflict="id").execute()
            mark_synced(event.id)
            pushed += 1
        except Exception:
            failed += 1
            with Session(engine) as session:
                current = session.get(SyncEvent, event.id)
                if current:
                    current.attempts += 1
                    session.add(current)
                    session.commit()
    return {"processed": len(events), "pushed": pushed, "failed": failed}
