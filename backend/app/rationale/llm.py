from __future__ import annotations

import logging

from app.config import ANTHROPIC_API_KEY, LLM_RATIONALE_TIMEOUT

log = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a friendly espresso coach giving brief, conversational feedback. "
    "You will receive a structured analysis of an espresso shot. "
    "Rephrase it naturally in 1-3 sentences — as if texting an enthusiast friend. "
    "You MUST preserve the recommended direction and magnitude exactly. "
    "Do NOT add new advice, disclaimers, or technical jargon the original lacks. "
    "Reply with ONLY the rephrased rationale, no preamble."
)

_USER_TEMPLATE = (
    "Reason: {reason_code}\n"
    "Direction: {direction}\n"
    "Magnitude: {magnitude_normalized}\n"
    "Facts: {facts}\n\n"
    "Template version (rephrase this):\n{template_rationale}"
)


def generate_llm_rationale(
    reason_code: str,
    facts: dict,
    direction: str,
    magnitude_normalized: float,
    template_rationale: str,
) -> str:
    """Call Anthropic to rephrase the template rationale conversationally.

    Raises on any failure — the caller is responsible for fallback.
    """
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError("anthropic package is not installed") from exc

    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    user_message = _USER_TEMPLATE.format(
        reason_code=reason_code,
        direction=direction,
        magnitude_normalized=magnitude_normalized,
        facts=facts,
        template_rationale=template_rationale,
    )

    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        timeout=LLM_RATIONALE_TIMEOUT,
    )

    response = client.messages.create(
        model="claude-haiku-4-20250414",
        max_tokens=256,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    text = response.content[0].text.strip()
    if not text:
        raise ValueError("LLM returned empty response")
    return text
