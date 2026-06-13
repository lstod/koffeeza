from __future__ import annotations

import os


def _bool_env(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).lower() in ("true", "1", "yes")


ENABLE_LLM_RATIONALE: bool = _bool_env("ENABLE_LLM_RATIONALE")
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
LLM_RATIONALE_MODEL: str = os.getenv("LLM_RATIONALE_MODEL", "claude-haiku-4-20250414")
LLM_RATIONALE_TIMEOUT: float = float(os.getenv("LLM_RATIONALE_TIMEOUT", "5.0"))
