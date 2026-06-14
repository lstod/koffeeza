from __future__ import annotations

import logging

from app.rationale.templates import render_rationale

log = logging.getLogger(__name__)

__all__ = ["get_rationale", "render_rationale"]


def get_rationale(
    reason_code: str,
    facts: dict,
    direction: str,
    magnitude_normalized: float,
) -> tuple[str, str]:
    """Return (rationale_text, source) with graceful LLM fallback.

    Always renders the template first. If the LLM feature flag is enabled,
    attempts an LLM rephrase; on any failure, falls back to the template.
    """
    template_text = render_rationale(reason_code, facts)

    from app.config import ENABLE_LLM_RATIONALE

    if not ENABLE_LLM_RATIONALE:
        return template_text, "template"

    try:
        from app.rationale.llm import generate_llm_rationale

        llm_text = generate_llm_rationale(
            reason_code=reason_code,
            facts=facts,
            direction=direction,
            magnitude_normalized=magnitude_normalized,
            template_rationale=template_text,
        )
        return llm_text, "llm"
    except Exception:
        log.warning("LLM rationale failed, falling back to template", exc_info=True)
        return template_text, "template"
