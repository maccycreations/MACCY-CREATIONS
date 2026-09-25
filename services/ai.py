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
    raise RuntimeError("Supported live adapters are OpenAI-compatible providers; configure provider-specific adapters before use")
