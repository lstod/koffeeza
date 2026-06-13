import ast
from dataclasses import dataclass
from pathlib import Path

import pytest

from app.adapter.core import Instruction, to_instruction
from app.adapter.seed import SEED_GRINDERS, seed_grinders
from app.enums import Direction, ScaleType


# ---------------------------------------------------------------------------
# Lightweight grinder stub (no DB dependency)
# ---------------------------------------------------------------------------


@dataclass
class FakeGrinder:
    scale_type: ScaleType
    step_native: float
    finer_is_lower: bool
    snap: float
    min_native: float | None = None
    max_native: float | None = None
    unit_label: str = ""


# Seed-table grinders used in spec tests
DEFAULT_GRINDER = FakeGrinder(ScaleType.STEPPED, 1.0, True, 1.0)
NICHE_ZERO = FakeGrinder(ScaleType.STEPLESS, 8.0, True, 5.0, unit_label="°")
COMANDANTE_C40 = FakeGrinder(ScaleType.CLICKS, 2.0, True, 1.0, unit_label="clicks")
BARATZA_ENCORE = FakeGrinder(ScaleType.STEPPED, 1.5, True, 1.0)
BARATZA_SETTE_30 = FakeGrinder(ScaleType.STEPPED, 1.0, True, 1.0, 1.0, 31.0)


# ---------------------------------------------------------------------------
# Spec tests (phase-3.md §3.4)
# ---------------------------------------------------------------------------


class TestSpecCases:
    """All five spec-mandated test cases."""

    def test_stepped_default_finer_moderate(self):
        """STEPPED default at 12, FINER MODERATE(1.0) → target 11, relative 1."""
        result = to_instruction(DEFAULT_GRINDER, 12.0, Direction.FINER, 1.0)
        assert result.target == 11
        assert result.relative == 1
        assert result.direction == "FINER"
        assert result.clamped is False

    def test_clicks_comandante_finer_moderate(self):
        """CLICKS Comandante, FINER MODERATE(1.0) → relative ~2 clicks, target None."""
        result = to_instruction(COMANDANTE_C40, None, Direction.FINER, 1.0)
        assert result.relative == 2
        assert result.target is None
        assert result.direction == "FINER"
        assert result.unit == "clicks"

    def test_stepless_niche_finer_moderate(self):
        """STEPLESS Niche, FINER MODERATE(1.0) → snap math: 1.0*8=8 → round(8/5)*5=10."""
        current = 30.0
        result = to_instruction(NICHE_ZERO, current, Direction.FINER, 1.0)
        assert result.relative == 10
        assert result.target == current - 10  # 20
        assert result.direction == "FINER"

    def test_clamp_at_min_finer(self):
        """Clamp: STEPPED at min_native, FINER → target stays at min, clamped True."""
        result = to_instruction(BARATZA_SETTE_30, 1.0, Direction.FINER, 1.0)
        assert result.target == 1
        assert result.clamped is True
        assert "finest usable setting" in result.text

    def test_direction_none(self):
        """Direction NONE → 'No change' instruction."""
        result = to_instruction(DEFAULT_GRINDER, 12.0, Direction.NONE, 0.0)
        assert "No change" in result.text
        assert result.direction is None
        assert result.relative is None
        assert result.target is None
        assert result.clamped is False


# ---------------------------------------------------------------------------
# Additional edge-case tests
# ---------------------------------------------------------------------------


class TestCoarserDirection:
    def test_coarser_finer_is_lower(self):
        """COARSER with finer_is_lower=True → target increases."""
        result = to_instruction(DEFAULT_GRINDER, 10.0, Direction.COARSER, 1.0)
        assert result.target == 11
        assert result.direction == "COARSER"

    def test_coarser_big_magnitude(self):
        result = to_instruction(DEFAULT_GRINDER, 5.0, Direction.COARSER, 2.5)
        assert result.target == 5 + round(2.5 * 1.0)
        assert result.relative == round(2.5 * 1.0)


class TestFinerIsLowerFalse:
    def test_inverted_finer(self):
        """Grinder where higher number = finer → FINER increases the setting."""
        grinder = FakeGrinder(ScaleType.STEPPED, 1.0, False, 1.0)
        result = to_instruction(grinder, 10.0, Direction.FINER, 1.0)
        assert result.target == 11
        assert result.direction == "FINER"

    def test_inverted_coarser(self):
        grinder = FakeGrinder(ScaleType.STEPPED, 1.0, False, 1.0)
        result = to_instruction(grinder, 10.0, Direction.COARSER, 1.0)
        assert result.target == 9
        assert result.direction == "COARSER"


class TestFloorGuard:
    def test_tiny_magnitude_snaps_to_one_step(self):
        """Very small magnitude that snaps to 0 gets bumped to one snap step."""
        result = to_instruction(DEFAULT_GRINDER, 10.0, Direction.FINER, 0.1)
        assert result.relative == 1  # snap=1, so floor guard → 1
        assert result.target == 9

    def test_tiny_magnitude_niche(self):
        """Niche snap=5: 0.1*8=0.8 → round(0.8/5)*5=0 → floor guard → 5."""
        result = to_instruction(NICHE_ZERO, 30.0, Direction.FINER, 0.1)
        assert result.relative == 5
        assert result.target == 25


class TestClamping:
    def test_clamp_max_coarser(self):
        """Clamp on max_native side (COARSER direction)."""
        result = to_instruction(BARATZA_SETTE_30, 31.0, Direction.COARSER, 1.0)
        assert result.target == 31
        assert result.clamped is True
        assert "finest usable setting" not in result.text

    def test_clamp_finer_includes_message(self):
        result = to_instruction(BARATZA_SETTE_30, 2.0, Direction.FINER, 5.0)
        assert result.clamped is True
        assert result.target == 1
        assert "finest usable setting" in result.text

    def test_no_clamp_within_range(self):
        result = to_instruction(BARATZA_SETTE_30, 15.0, Direction.FINER, 1.0)
        assert result.clamped is False
        assert result.target == 14


class TestClicksNoTarget:
    def test_clicks_coarser(self):
        result = to_instruction(COMANDANTE_C40, None, Direction.COARSER, 1.0)
        assert result.target is None
        assert result.relative == 2
        assert result.direction == "COARSER"


class TestNoCurrentNative:
    def test_stepped_without_current(self):
        """STEPPED/STEPLESS without current_native still returns relative delta."""
        result = to_instruction(DEFAULT_GRINDER, None, Direction.FINER, 1.0)
        assert result.relative == 1
        assert result.target is None
        assert result.clamped is False


# ---------------------------------------------------------------------------
# Seed profiles
# ---------------------------------------------------------------------------


class TestSeedProfiles:
    def test_seed_count(self):
        assert len(SEED_GRINDERS) == 5

    def test_seed_all_have_required_keys(self):
        required = {"brand", "model", "scale_type", "step_native", "finer_is_lower", "snap", "unit_label"}
        for profile in SEED_GRINDERS:
            assert required.issubset(profile.keys()), f"Missing keys in {profile['brand']} {profile['model']}"

    def test_seed_scale_types_cover_all(self):
        types = {p["scale_type"] for p in SEED_GRINDERS}
        assert types == {ScaleType.STEPPED, ScaleType.CLICKS, ScaleType.STEPLESS}

    def test_sette_30_has_bounds(self):
        sette = next(p for p in SEED_GRINDERS if p["model"] == "Sette 30")
        assert sette["min_native"] == 1.0
        assert sette["max_native"] == 31.0

    def test_seed_grinders_inserts(self, db, test_user):
        """seed_grinders() populates an empty table."""
        count = seed_grinders(db, user_id=test_user.id)
        assert count == 5

    def test_seed_grinders_idempotent(self, db, test_user):
        """Calling seed_grinders() twice inserts only once."""
        seed_grinders(db, user_id=test_user.id)
        count = seed_grinders(db, user_id=test_user.id)
        assert count == 0


# ---------------------------------------------------------------------------
# Purity check — adapter must not import DB or FastAPI
# ---------------------------------------------------------------------------


class TestPurity:
    def test_no_forbidden_imports(self):
        source = Path(__file__).resolve().parents[2] / "app" / "adapter" / "core.py"
        tree = ast.parse(source.read_text())
        forbidden = {"sqlalchemy", "fastapi", "app.database", "app.models"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in forbidden, (
                        f"Forbidden import: {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in forbidden, (
                    f"Forbidden import: {node.module}"
                )
