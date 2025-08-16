"""Minimal llama.cpp provider using an HTTP endpoint.

This module expects a llama.cpp server to be running locally. The
endpoint is read from the ``LLAMA_CPP_BASE_URL`` environment variable
and defaults to ``http://localhost:8080``. The server is expected to
expose a ``/v1/completions`` endpoint accepting a JSON payload with a
``prompt`` field and returning ``{"completion": <str>}``.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Optional


def _extract_text(data: dict) -> str:
    """Extract text from either dummy or OpenAI-style responses."""
    # Dummy server used in tests
    if "completion" in data and isinstance(data["completion"], str):
        return data["completion"]
    # OpenAI-style /v1/completions
    choices = data.get("choices") or []
    if choices:
        first = choices[0]
        if isinstance(first, dict):
            if "text" in first and isinstance(first["text"], str):
                return first["text"]
            msg = first.get("message")
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"]
    return ""


def call(prompt: str, base_url: Optional[str] = None) -> str:
    """Call a llama.cpp server and return the completion string.

    Accepts both the dummy test server shape and OpenAI-style responses.
    """
    base = base_url or os.environ.get("LLAMA_CPP_BASE_URL", "http://localhost:8080")
    payload = {"prompt": prompt}
    req = urllib.request.Request(
        f"{base}/v1/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return _extract_text(data)
