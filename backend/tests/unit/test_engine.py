import ast
import importlib
from datetime import date, timedelta
from pathlib import Path

import pytest

from app.engine.core import Decision, EngineConfig, ShotInput, recommend
from app.enums import Confidence, Direction, Intensity, ReasonCode, Taste


# ---------------------------------------------------------------------------
# Spec table (phase-2.md)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dose, yld, time, taste, exp_dir, exp_mag, exp_reason",
    [
        # Row 1: far below window → FLOW_TOO_FAST
        (18, 36, 18, Taste.SOUR, Direction.FINER, 2.5, ReasonCode.FLOW_TOO_FAST),
        # Row 2: below window → FLOW_FAST
        (18, 36, 21, Taste.SOUR, Direction.FINER, 1.0, ReasonCode.FLOW_FAST),
        # Row 3: fast + bitter → CHANNELING_SUSPECTED
        (18, 36, 22, Taste.BITTER, Direction.NONE, 0, ReasonCode.CHANNELING_SUSPECTED),
        # Row 4: in-window balanced → DIALED_IN
        (18, 36, 28, Taste.BALANCED, Direction.NONE, 0, ReasonCode.DIALED_IN),
        # Row 5: in-window sour → TASTE_SOUR
        (18, 36, 28, Taste.SOUR, Direction.FINER, 0.5, ReasonCode.TASTE_SOUR),
        # Row 6: in-window bitter → TASTE_BITTER
        (18, 36, 28, Taste.BITTER, Direction.COARSER, 0.5, ReasonCode.TASTE_BITTER),
        # Row 7: far above window → FLOW_TOO_SLOW
        (18, 36, 45, Taste.BITTER, Direction.COARSER, 2.5, ReasonCode.FLOW_TOO_SLOW),
        # Row 8: slow + sour → CHANNELING_SUSPECTED
        (18, 36, 38, Taste.SOUR, Direction.NONE, 0, ReasonCode.CHANNELING_SUSPECTED),
    ],
    ids=[
        "flow_too_fast",
        "flow_fast",
        "channeling_fast_bitter",
        "dialed_in",
        "taste_sour",
        "taste_bitter",
        "flow_too_slow",
        "channeling_slow_sour",
    ],
)
def test_spec_table(dose, yld, time, taste, exp_dir, exp_mag, exp_reason):
    shot = ShotInput(dose_g=dose, yield_g=yld, time_s=time, taste=taste)
    d = recommend(shot)
    assert d.direction == exp_dir
    assert d.magnitude_normalized == exp_mag
    assert d.reason_code == exp_reason


def test_spec_row9_ratio_shift():
    """Row 9: ratio 3.0 shifts window to [32, 39]. 28s is below t_lo → FLOW_FAST."""
    shot = ShotInput(dose_g=18, yield_g=54, time_s=28, taste=Taste.BITTER)
    config = EngineConfig(target_ratio=3.0)
    d = recommend(shot, config)
    assert d.direction == Direction.FINER
    assert d.magnitude_normalized == 1.0
    assert d.reason_code == ReasonCode.FLOW_FAST


# ---------------------------------------------------------------------------
# Channeling details
# ---------------------------------------------------------------------------

def test_channeling_slow_weak():
    """slow + WEAK also triggers channeling."""
    shot = ShotInput(dose_g=18, yield_g=36, time_s=35, taste=Taste.WEAK)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.CHANNELING_SUSPECTED
    assert d.direction == Direction.NONE


# ---------------------------------------------------------------------------
# Intensity bump
# ---------------------------------------------------------------------------

def test_intensity_strong_bumps_small_to_moderate():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.SOUR, intensity=Intensity.STRONG)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.TASTE_SOUR
    assert d.magnitude_normalized == 1.0  # SMALL bumped to MODERATE


def test_intensity_mild_keeps_small():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.SOUR, intensity=Intensity.MILD)
    d = recommend(shot)
    assert d.magnitude_normalized == 0.5


def test_intensity_strong_no_bump_on_dialed_in():
    """STRONG intensity doesn't bump DIALED_IN (magnitude is 0, not SMALL)."""
    shot = ShotInput(
        dose_g=18, yield_g=36, time_s=28, taste=Taste.BALANCED, intensity=Intensity.STRONG,
    )
    d = recommend(shot)
    assert d.magnitude_normalized == 0
    assert d.reason_code == ReasonCode.DIALED_IN


# ---------------------------------------------------------------------------
# Freshness notes
# ---------------------------------------------------------------------------

def test_freshness_degassing_note():
    roast = date.today() - timedelta(days=3)
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.SOUR, roast_date=roast)
    d = recommend(shot)
    assert any("degassing" in n.lower() for n in d.secondary_notes)


def test_freshness_staleness_note():
    roast = date.today() - timedelta(days=35)
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.SOUR, roast_date=roast)
    d = recommend(shot)
    assert any("staleness" in n.lower() or "stale" in n.lower() for n in d.secondary_notes)


def test_freshness_no_note_in_range():
    roast = date.today() - timedelta(days=14)
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.SOUR, roast_date=roast)
    d = recommend(shot)
    assert not any("degassing" in n.lower() or "stale" in n.lower() for n in d.secondary_notes)


def test_freshness_no_note_when_no_roast_date():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.SOUR)
    d = recommend(shot)
    assert d.secondary_notes == []


# ---------------------------------------------------------------------------
# Window boundary tests
# ---------------------------------------------------------------------------

def test_exact_t_lo_is_in_window():
    """time == t_lo should be in-window, not flow fault."""
    shot = ShotInput(dose_g=18, yield_g=36, time_s=25, taste=Taste.BALANCED)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.DIALED_IN


def test_exact_t_hi_is_in_window():
    """time == t_hi should be in-window, not flow fault."""
    shot = ShotInput(dose_g=18, yield_g=36, time_s=32, taste=Taste.BALANCED)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.DIALED_IN


def test_just_below_t_lo_is_flow_fast():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=24.9, taste=Taste.BALANCED)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.FLOW_FAST


def test_just_above_t_hi_is_flow_slow():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=32.1, taste=Taste.BALANCED)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.FLOW_SLOW


# ---------------------------------------------------------------------------
# Taste variants
# ---------------------------------------------------------------------------

def test_taste_weak_has_ratio_note():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.WEAK)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.TASTE_WEAK
    assert d.direction == Direction.FINER
    assert any("ratio" in n.lower() for n in d.secondary_notes)


def test_taste_astringent_has_channeling_note():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.ASTRINGENT)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.TASTE_ASTRINGENT
    assert d.direction == Direction.COARSER
    assert d.confidence == Confidence.LOW
    assert any("channeling" in n.lower() for n in d.secondary_notes)


# ---------------------------------------------------------------------------
# Flow fault notes
# ---------------------------------------------------------------------------

def test_flow_too_slow_has_puck_prep_note():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=45, taste=Taste.BITTER)
    d = recommend(shot)
    assert d.reason_code == ReasonCode.FLOW_TOO_SLOW
    assert any("puck prep" in n.lower() for n in d.secondary_notes)


# ---------------------------------------------------------------------------
# Facts dict
# ---------------------------------------------------------------------------

def test_facts_populated():
    shot = ShotInput(dose_g=18, yield_g=36, time_s=28, taste=Taste.BALANCED)
    d = recommend(shot)
    assert d.facts["ratio"] == pytest.approx(2.0)
    assert d.facts["time_s"] == 28
    assert d.facts["t_lo"] == 25
    assert d.facts["t_hi"] == 32
    assert d.facts["taste"] == "BALANCED"


# ---------------------------------------------------------------------------
# Purity check — engine must not depend on DB, FastAPI, or external services
# ---------------------------------------------------------------------------

def test_engine_purity():
    """Verify engine/core.py has no imports from sqlalchemy, fastapi, app.database, or app.models."""
    engine_path = Path(__file__).resolve().parents[2] / "app" / "engine" / "core.py"
    tree = ast.parse(engine_path.read_text())

    forbidden = {"sqlalchemy", "fastapi", "app.database", "app.models"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not any(
                    alias.name == f or alias.name.startswith(f + ".") for f in forbidden
                ), f"Forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert not any(
                node.module == f or node.module.startswith(f + ".") for f in forbidden
            ), f"Forbidden import from: {node.module}"

    mod = importlib.import_module("app.engine.core")
    for attr in dir(mod):
        obj = getattr(mod, attr)
        if hasattr(obj, "__module__") and obj.__module__:
            assert not any(
                obj.__module__.startswith(f) for f in forbidden
            ), f"{attr} originates from forbidden module {obj.__module__}"
