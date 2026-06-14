from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.enums import ReasonCode
from app.rationale import get_rationale, render_rationale

SAMPLE_FACTS = {"time_s": 22.0, "t_lo": 25.0, "t_hi": 32.0, "ratio": 2.0, "taste": None}


# ── Test 1: LLM disabled (default) returns template ─────────────────────────


def test_flag_off_returns_template(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM_RATIONALE", "false")
    import app.config

    monkeypatch.setattr(app.config, "ENABLE_LLM_RATIONALE", False)

    text, source = get_rationale(
        reason_code=ReasonCode.FLOW_FAST,
        facts=SAMPLE_FACTS,
        direction="FINER",
        magnitude_normalized=1.0,
    )
    expected = render_rationale(ReasonCode.FLOW_FAST, SAMPLE_FACTS)
    assert text == expected
    assert source == "template"


# ── Test 2: LLM enabled but API call fails → fallback ───────────────────────


def test_llm_api_error_falls_back_to_template(monkeypatch):
    import app.config

    monkeypatch.setattr(app.config, "ENABLE_LLM_RATIONALE", True)

    with patch(
        "app.rationale.llm.generate_llm_rationale",
        side_effect=RuntimeError("API error"),
    ):
        text, source = get_rationale(
            reason_code=ReasonCode.FLOW_FAST,
            facts=SAMPLE_FACTS,
            direction="FINER",
            magnitude_normalized=1.0,
        )
    expected = render_rationale(ReasonCode.FLOW_FAST, SAMPLE_FACTS)
    assert text == expected
    assert source == "template"


# ── Test 3: LLM enabled and succeeds → returns LLM text ─────────────────────


def test_llm_success_returns_llm_text(monkeypatch):
    import app.config

    monkeypatch.setattr(app.config, "ENABLE_LLM_RATIONALE", True)

    rephrased = "Hey, that shot flew through! Try grinding a bit finer next time."

    with patch(
        "app.rationale.llm.generate_llm_rationale",
        return_value=rephrased,
    ):
        text, source = get_rationale(
            reason_code=ReasonCode.FLOW_FAST,
            facts=SAMPLE_FACTS,
            direction="FINER",
            magnitude_normalized=1.0,
        )
    assert text == rephrased
    assert source == "llm"


# ── Test 4: LLM enabled but anthropic not installed → fallback ───────────────


def test_import_error_falls_back_to_template(monkeypatch):
    import app.config

    monkeypatch.setattr(app.config, "ENABLE_LLM_RATIONALE", True)

    with patch(
        "app.rationale.llm.generate_llm_rationale",
        side_effect=RuntimeError("anthropic package is not installed"),
    ):
        text, source = get_rationale(
            reason_code=ReasonCode.TASTE_SOUR,
            facts=SAMPLE_FACTS,
            direction="FINER",
            magnitude_normalized=0.5,
        )
    expected = render_rationale(ReasonCode.TASTE_SOUR, SAMPLE_FACTS)
    assert text == expected
    assert source == "template"


# ── Test 5: generate_llm_rationale unit tests ────────────────────────────────


def test_generate_raises_without_api_key(monkeypatch):
    import app.config

    monkeypatch.setattr(app.config, "ANTHROPIC_API_KEY", None)

    mock_anthropic = MagicMock()
    with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
        from app.rationale.llm import generate_llm_rationale

        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is not set"):
            generate_llm_rationale(
                reason_code=ReasonCode.FLOW_FAST,
                facts=SAMPLE_FACTS,
                direction="FINER",
                magnitude_normalized=1.0,
                template_rationale="test",
            )


def test_generate_raises_without_anthropic_package(monkeypatch):
    import app.config

    monkeypatch.setattr(app.config, "ANTHROPIC_API_KEY", "sk-test")

    import builtins

    real_import = builtins.__import__

    def _mock_import(name, *args, **kwargs):
        if name == "anthropic":
            raise ImportError("No module named 'anthropic'")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=_mock_import):
        from app.rationale.llm import generate_llm_rationale

        with pytest.raises(RuntimeError, match="anthropic package is not installed"):
            generate_llm_rationale(
                reason_code=ReasonCode.FLOW_FAST,
                facts=SAMPLE_FACTS,
                direction="FINER",
                magnitude_normalized=1.0,
                template_rationale="test",
            )


# ── Test 6: Direction/magnitude integrity at API level ───────────────────────


def test_shot_response_preserves_engine_direction(client, create_bean, create_grinder, create_machine, monkeypatch):
    """The LLM only controls rationale text; direction/magnitude come from the engine."""
    import app.config

    monkeypatch.setattr(app.config, "ENABLE_LLM_RATIONALE", True)

    rephrased = "Whoa, that was way too fast! Crank that grind much finer."

    bean = create_bean()
    grinder = create_grinder()
    machine = create_machine()

    with patch(
        "app.rationale.llm.generate_llm_rationale",
        return_value=rephrased,
    ):
        resp = client.post("/shots", json={
            "bean_id": bean.id,
            "grinder_id": grinder.id,
            "machine_id": machine.id,
            "grind_setting_native": "5.0",
            "dose_g": 18.0,
            "yield_g": 36.0,
            "time_s": 15.0,
            "taste": None,
        })

    assert resp.status_code == 201
    data = resp.json()
    assert data["direction"] == "FINER"
    assert data["magnitude_normalized"] == 2.5
    assert data["rationale"] == rephrased
    assert data["rationale_source"] == "llm"


def test_shot_response_template_source_by_default(client, create_bean, create_grinder, create_machine):
    """Without the LLM flag, rationale_source is 'template'."""
    bean = create_bean()
    grinder = create_grinder()
    machine = create_machine()

    resp = client.post("/shots", json={
        "bean_id": bean.id,
        "grinder_id": grinder.id,
        "machine_id": machine.id,
        "grind_setting_native": "5.0",
        "dose_g": 18.0,
        "yield_g": 36.0,
        "time_s": 28.0,
        "taste": "BALANCED",
    })

    assert resp.status_code == 201
    data = resp.json()
    assert data["rationale_source"] == "template"
    assert "dialed in" in data["rationale"].lower()
