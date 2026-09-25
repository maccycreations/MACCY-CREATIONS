from __future__ import annotations

import re
from collections import Counter

STOPWORDS = {"and", "the", "with", "for", "from", "that", "this", "you", "your", "are", "into", "our", "will", "have", "has"}
ACTION_VERBS = {"built", "created", "designed", "led", "improved", "delivered", "automated", "reduced", "increased", "implemented", "developed", "managed"}


def words(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[a-zA-Z][a-zA-Z+#.-]{1,}", text)]


def analyze_resume(resume_text: str, job_description: str = "") -> dict:
    resume = set(words(resume_text))
    job_terms = [word for word in words(job_description) if word not in STOPWORDS]
    required = set(job_terms)
    matched = sorted(resume & required)
    missing = sorted(required - resume)
    keyword_score = round((len(matched) / len(required)) * 100) if required else 0
    verb_hits = len(set(words(resume_text)) & ACTION_VERBS)
    formatting_score = 100 if resume_text.strip() and "@" in resume_text else 65 if resume_text.strip() else 0
    action_score = min(100, verb_hits * 12)
    overall = round(keyword_score * 0.55 + formatting_score * 0.25 + action_score * 0.20)
    return {"overall_score": overall, "keyword_score": keyword_score, "formatting_score": formatting_score, "action_verb_score": action_score, "matched_keywords": matched[:100], "missing_keywords": missing[:100]}
