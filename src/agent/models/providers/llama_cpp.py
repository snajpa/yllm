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


def call(prompt: str) -> str:
    base = os.environ.get("LLAMA_CPP_BASE_URL", "http://localhost:8080")
    req = urllib.request.Request(
        f"{base}/v1/completions",
        data=json.dumps({"prompt": prompt}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return data.get("completion", "")
