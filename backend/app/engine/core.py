from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.enums import Confidence, Direction, Intensity, ReasonCode, Taste

BIG = 2.5
MODERATE = 1.0
SMALL = 0.5


@dataclass(frozen=True)
class ShotInput:
    dose_g: float
    yield_g: float
    time_s: float
    taste: Taste
    intensity: Intensity | None = None
    roast_date: date | None = None


@dataclass(frozen=True)
class EngineConfig:
    target_ratio: float = 2.0


_DEFAULT_CONFIG = EngineConfig()


@dataclass(frozen=True)
class Decision:
    direction: Direction
    magnitude_normalized: float
    reason_code: ReasonCode
    confidence: Confidence
    facts: dict = field(default_factory=dict)
    secondary_notes: list[str] = field(default_factory=list)


def _time_window(target_ratio: float) -> tuple[float, float]:
    offset = (target_ratio - 2.0) * 7
    return 25 + offset, 32 + offset


def _is_fast(time_s: float, t_lo: float) -> bool:
    return time_s < t_lo


def _is_slow(time_s: float, t_hi: float) -> bool:
    return time_s > t_hi


def recommend(shot: ShotInput, config: EngineConfig = _DEFAULT_CONFIG) -> Decision:
    ratio = shot.yield_g / shot.dose_g
    t_lo, t_hi = _time_window(config.target_ratio)
    facts = {
        "ratio": ratio,
        "time_s": shot.time_s,
        "t_lo": t_lo,
        "t_hi": t_hi,
        "taste": shot.taste.value,
    }

    # Channeling uses the standard window (ratio 2.0) — contradictory taste is
    # only meaningful relative to absolute extraction speed, not a shifted target.
    base_lo, base_hi = _time_window(2.0)
    ch_fast = _is_fast(shot.time_s, base_lo)
    ch_slow = _is_slow(shot.time_s, base_hi)

    # Step A — Channeling check
    if ch_fast and shot.taste == Taste.BITTER:
        return Decision(Direction.NONE, 0, ReasonCode.CHANNELING_SUSPECTED, Confidence.LOW, facts)
    if ch_slow and shot.taste in (Taste.SOUR, Taste.WEAK):
        return Decision(Direction.NONE, 0, ReasonCode.CHANNELING_SUSPECTED, Confidence.LOW, facts)

    fast = _is_fast(shot.time_s, t_lo)
    slow = _is_slow(shot.time_s, t_hi)

    # Step B — Flow faults
    if shot.time_s < t_lo - 5:
        return Decision(Direction.FINER, BIG, ReasonCode.FLOW_TOO_FAST, Confidence.HIGH, facts)
    if shot.time_s > t_hi + 8:
        return Decision(
            Direction.COARSER,
            BIG,
            ReasonCode.FLOW_TOO_SLOW,
            Confidence.HIGH,
            facts,
            ["Check puck prep — distribution and tamp consistency."],
        )
    if fast:
        return Decision(Direction.FINER, MODERATE, ReasonCode.FLOW_FAST, Confidence.MEDIUM, facts)
    if slow:
        return Decision(Direction.COARSER, MODERATE, ReasonCode.FLOW_SLOW, Confidence.MEDIUM, facts)

    # Step C — In-window taste
    notes: list[str] = []
    direction = Direction.NONE
    magnitude = 0.0
    confidence = Confidence.HIGH
    reason = ReasonCode.DIALED_IN

    if shot.taste == Taste.BALANCED:
        pass
    elif shot.taste == Taste.SOUR:
        direction, magnitude, confidence, reason = (
            Direction.FINER,
            SMALL,
            Confidence.MEDIUM,
            ReasonCode.TASTE_SOUR,
        )
    elif shot.taste == Taste.BITTER:
        direction, magnitude, confidence, reason = (
            Direction.COARSER,
            SMALL,
            Confidence.MEDIUM,
            ReasonCode.TASTE_BITTER,
        )
    elif shot.taste == Taste.WEAK:
        direction, magnitude, confidence, reason = (
            Direction.FINER,
            SMALL,
            Confidence.MEDIUM,
            ReasonCode.TASTE_WEAK,
        )
        notes.append("Consider lowering the brew ratio for more body.")
    elif shot.taste == Taste.ASTRINGENT:
        direction, magnitude, confidence, reason = (
            Direction.COARSER,
            SMALL,
            Confidence.LOW,
            ReasonCode.TASTE_ASTRINGENT,
        )
        notes.append("Astringency can also indicate channeling — check puck prep.")

    # Intensity bump: STRONG bumps SMALL → MODERATE
    if shot.intensity == Intensity.STRONG and magnitude == SMALL:
        magnitude = MODERATE

    # Step D — Freshness modifier
    if shot.roast_date is not None:
        age_days = (date.today() - shot.roast_date).days
        if age_days < 5:
            notes.append(
                f"Beans are {age_days} days off roast — CO₂ degassing may cause uneven extraction."
            )
        elif age_days > 28:
            notes.append(f"Beans are {age_days} days off roast — staleness may mute flavors.")

    return Decision(direction, magnitude, reason, confidence, facts, notes)
