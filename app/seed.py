from __future__ import annotations

from app.database import engine
from app.models import AIConfig, Application, CareerTrack, JobListing, Resume, Roadmap, Skill, UserProfile
from sqlmodel import Session, select


def seed_database() -> None:
    with Session(engine) as session:
        existing_user = session.exec(select(UserProfile).limit(1)).first()
        if existing_user is None:
            user = UserProfile(full_name="Demo User", email="demo@maccy.creations", target_role="AI Engineer")
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            user = existing_user

        if session.exec(select(Skill).limit(1)).first() is None:
            skills = [
                Skill(name="Python", category="Software Engineering", proficiency="Expert", progress=90, owner_id=user.id),
                Skill(name="FastAPI", category="Software Engineering", proficiency="Advanced", progress=85, owner_id=user.id),
                Skill(name="SQL", category="Data Science & AI", proficiency="Advanced", progress=80, owner_id=user.id),
                Skill(name="Machine Learning", category="Data Science & AI", proficiency="Intermediate", progress=70, owner_id=user.id),
                Skill(name="AWS", category="Cloud & DevOps", proficiency="Intermediate", progress=68, owner_id=user.id),
            ]
            session.add_all(skills)

        if session.exec(select(CareerTrack).limit(1)).first() is None:
            career_tracks = [
                CareerTrack(
                    title="AI Engineer",
                    level="Mid",
                    skills="Python, FastAPI, ML, SQL",
                    salary_range="$120k - $180k",
                    demand="High",
                    resources="Coursera, DeepLearning.AI, AWS Skill Builder",
                    description="Build production AI apps with strong software engineering fundamentals.",
                ),
                CareerTrack(
                    title="Data Scientist",
                    level="Mid",
                    skills="Python, SQL, ML, Statistics",
                    salary_range="$110k - $170k",
                    demand="High",
                    resources="Kaggle, Udemy, Coursera",
                    description="Translate data into machine learning products and business impact.",
                ),
                CareerTrack(
                    title="Full-Stack Developer",
                    level="Mid",
                    skills="Python, FastAPI, SQL, Frontend fundamentals",
                    salary_range="$100k - $160k",
                    demand="Very High",
                    resources="Roadmap.sh, freeCodeCamp, MDN",
                    description="Ship end-to-end web products with APIs and internal tooling.",
                ),
            ]
            session.add_all(career_tracks)

        if session.exec(select(Roadmap).limit(1)).first() is None:
            roadmap = Roadmap(
                title="AI Engineer Roadmap",
                target_role="AI Engineer",
                steps="[\"Strengthen Python and API engineering\",\"Build ML fundamentals and model evaluation\",\"Create production AI workflows\",\"Deploy with cloud and monitoring\"]",
                owner_id=user.id,
            )
            session.add(roadmap)

        if session.exec(select(Resume).limit(1)).first() is None:
            resume = Resume(
                title="AI Engineer Resume",
                career_role="AI Engineer",
                summary="Experienced in Python, ML systems, and product delivery.",
                ats_score=92,
                file_url="https://example.com/demo-resume.pdf",
                owner_id=user.id,
            )
            session.add(resume)

        if session.exec(select(JobListing).limit(1)).first() is None:
            jobs = [
                JobListing(company="Google", title="AI Engineer", location="Remote", remote=True, salary="$150k - $210k", source="Public", owner_id=user.id),
                JobListing(company="Microsoft", title="Software Engineer", location="Hybrid", remote=False, salary="$130k - $190k", source="Public", owner_id=user.id),
            ]
            session.add_all(jobs)

        if session.exec(select(Application).limit(1)).first() is None:
            app_record = Application(company="Google", title="AI Engineer", status="Saved", notes="Strong fit for Python + AI work.", owner_id=user.id)
            session.add(app_record)

        if session.exec(select(AIConfig).limit(1)).first() is None:
            session.add(AIConfig(provider="OpenAI", model_name="gpt-4o-mini", api_key_hint="sk-***", enabled=True, owner_id=user.id))

        session.commit()
