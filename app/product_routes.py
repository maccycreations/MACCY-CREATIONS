from __future__ import annotations

import os
from typing import Any

import httpx


async def complete(provider: str, prompt: str, model: str | None = None) -> dict[str, Any]:
    provider = provider.lower()
    if provider in {"openai", "grok", "custom"}:
        key = os.getenv("XAI_API_KEY" if provider == "grok" else "OPENAI_API_KEY" if provider == "openai" else "CUSTOM_AGENT_API_KEY")
        base = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1") if provider == "grok" else os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not key:
            raise RuntimeError("Provider API key is not configured")
        payload = {"model": model or ("grok-3-mini" if provider == "grok" else "gpt-4o-mini"), "messages": [{"role": "user", "content": prompt}]}
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(f"{base}/chat/completions", headers={"Authorization": f"Bearer {key}"}, json=payload)
            response.raise_for_status()
            data = response.json()
            return {"provider": provider, "text": data["choices"][0]["message"]["content"]}
    if provider == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if not key: raise RuntimeError("GEMINI_API_KEY is not configured")
        selected = model or "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected}:generateContent?key={key}"
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
            response.raise_for_status()
            data = response.json()
            return {"provider": provider, "text": data["candidates"][0]["content"]["parts"][0]["text"]}
    if provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key: raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": key, "anthropic-version": "2023-06-01"}, json={"model": model or "claude-3-5-haiku-latest", "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]})
            response.raise_for_status()
            data = response.json()
            return {"provider": provider, "text": data["content"][0]["text"]}
    raise RuntimeError("Unsupported provider")
