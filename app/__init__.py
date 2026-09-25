from __future__ import annotations

from app.database import init_db
from app.seed import seed_database

init_db()
seed_database()
