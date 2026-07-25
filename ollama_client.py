from __future__ import annotations

import json
from typing import Iterator

import requests


def stream_chat(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    base_url: str,
    timeout: int = 120,
) -> Iterator[str]:
    """Stream chat response chunks from Ollama and yield text fragments."""
    url = base_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "stream": True,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    with requests.post(url, json=payload, stream=True, timeout=timeout) as response:
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                data = json.loads(line)
            except (ValueError, json.JSONDecodeError):
                continue

            message = data.get("message") or {}
            content = message.get("content") or ""
            if content:
                yield content


def check_ollama_health(base_url: str, timeout: int = 5) -> tuple[bool, str]:
    """Return Ollama reachability status and a human-readable message."""
    try:
        response = requests.get(base_url.rstrip("/") + "/api/tags", timeout=timeout)
        response.raise_for_status()
        return True, "Connected to Ollama"
    except requests.RequestException as exc:
        return False, f"Ollama unavailable: {exc}"
