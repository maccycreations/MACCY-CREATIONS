from __future__ import annotations

import hashlib
from typing import Any

import httpx
from sqlmodel import Session, select

from app.database import engine
from app.models import JobListing

PUBLIC_SOURCES = {
    "remoteok": "https://remoteok.com/api",
    "arbeitnow": "https://www.arbeitnow.com/api/job-board-api",
}


def normalize(source: str, row: dict[str, Any]) -> JobListing:
    title = row.get("position") or row.get("title") or "Untitled role"
    company = row.get("company_name") or row.get("company") or "Unknown company"
    url = row.get("url") or row.get("job_url") or ""
    external = str(row.get("id") or row.get("slug") or url or f"{company}:{title}")
    external_id = hashlib.sha256(f"{source}:{external}".encode()).hexdigest()
    return JobListing(external_id=external_id, company=company, title=title, location=row.get("location") or "Remote", remote=True, salary=row.get("salary"), description=row.get("description"), url=url, source=source)


async def fetch_jobs(query: str = "python", remote_only: bool = False) -> list[JobListing]:
    found: list[JobListing] = []
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "MACCY-CREATIONS/1.0"}) as client:
        for source, endpoint in PUBLIC_SOURCES.items():
            try:
                response = await client.get(endpoint)
                response.raise_for_status()
                data = response.json()
                rows = data.get("data", data) if isinstance(data, dict) else data
                for row in rows if isinstance(rows, list) else []:
                    job = normalize(source, row)
                    haystack = f"{job.title} {job.company} {job.description or ''}".lower()
                    if query.lower() in haystack and (not remote_only or job.remote):
                        found.append(job)
            except (httpx.HTTPError, ValueError, TypeError):
                continue
    with Session(engine) as session:
        for job in found:
            if not session.exec(select(JobListing).where(JobListing.external_id == job.external_id)).first():
                session.add(job)
        session.commit()
    return found
