"""GitHub Models API access for cursorEval dynamic commands."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

_GITHUB_MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"


def get_token() -> str | None:
    return (
        os.environ.get("GITHUB_MODELS_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
    )


def call_model(messages: list[dict], model: str, token: str) -> str:
    payload = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(
        _GITHUB_MODELS_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: {exc.reason}") from exc
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError(str(exc)) from exc
