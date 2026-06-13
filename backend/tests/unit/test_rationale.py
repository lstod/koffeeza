import pytest

from app.enums import ReasonCode
from app.rationale import render_rationale

SAMPLE_FACTS = {"time_s": 28.0, "t_lo": 25.0, "t_hi": 32.0, "ratio": 2.0, "taste": "BALANCED"}


def test_flow_too_fast():
    result = render_rationale(ReasonCode.FLOW_TOO_FAST, {**SAMPLE_FACTS, "time_s": 18.0})
    assert "18.0s" in result
    assert "25.0-32.0s" in result
    assert "finer" in result.lower()


def test_flow_fast():
    result = render_rationale(ReasonCode.FLOW_FAST, {**SAMPLE_FACTS, "time_s": 22.0})
    assert "22.0s" in result
    assert "finer" in result.lower()


def test_flow_too_slow():
    result = render_rationale(ReasonCode.FLOW_TOO_SLOW, {**SAMPLE_FACTS, "time_s": 45.0})
    assert "45.0s" in result
    assert "coarser" in result.lower()


def test_flow_slow():
    result = render_rationale(ReasonCode.FLOW_SLOW, {**SAMPLE_FACTS, "time_s": 35.0})
    assert "35.0s" in result
    assert "coarser" in result.lower()


def test_dialed_in():
    result = render_rationale(ReasonCode.DIALED_IN, SAMPLE_FACTS)
    assert "28.0s" in result
    assert "dialed in" in result.lower()


def test_taste_sour():
    result = render_rationale(ReasonCode.TASTE_SOUR, SAMPLE_FACTS)
    assert "28.0s" in result
    assert "sour" in result.lower()
    assert "finer" in result.lower()


def test_taste_bitter():
    result = render_rationale(ReasonCode.TASTE_BITTER, SAMPLE_FACTS)
    assert "28.0s" in result
    assert "bitter" in result.lower()
    assert "coarser" in result.lower()


def test_taste_weak():
    result = render_rationale(ReasonCode.TASTE_WEAK, SAMPLE_FACTS)
    assert "weak" in result.lower()
    assert "finer" in result.lower()


def test_taste_astringent():
    result = render_rationale(ReasonCode.TASTE_ASTRINGENT, SAMPLE_FACTS)
    assert "astringency" in result.lower()
    assert "channeling" in result.lower()


def test_channeling_suspected():
    result = render_rationale(ReasonCode.CHANNELING_SUSPECTED, SAMPLE_FACTS)
    assert "disagree" in result.lower()
    assert "grind" in result.lower()


def test_unknown_reason_code_raises():
    with pytest.raises(KeyError):
        render_rationale("NOT_A_REAL_CODE", SAMPLE_FACTS)
