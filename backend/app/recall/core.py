from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.enums import ReasonCode
from app.models.shot import Shot

_GENERIC_DOSE = 18.0
_GENERIC_YIELD = 36.0
_GENERIC_TIME = 28.0


@dataclass(frozen=True)
class RecallResult:
    confidence_label: str  # EXACT | APPROXIMATE | GENERIC
    source_tier: int  # 1-5
    grind_setting_native: str | None
    dose_g: float
    yield_g: float
    time_s: float
    shot_id: int | None  # None for GENERIC


def _result_from_shot(shot: Shot, tier: int) -> RecallResult:
    return RecallResult(
        confidence_label="EXACT",
        source_tier=tier,
        grind_setting_native=shot.grind_setting_native,
        dose_g=shot.dose_g,
        yield_g=shot.yield_g,
        time_s=shot.time_s,
        shot_id=shot.id,
    )


def _generic() -> RecallResult:
    return RecallResult(
        confidence_label="GENERIC",
        source_tier=5,
        grind_setting_native=None,
        dose_g=_GENERIC_DOSE,
        yield_g=_GENERIC_YIELD,
        time_s=_GENERIC_TIME,
        shot_id=None,
    )


def recall(db: Session, bean_id: int, grinder_id: int, machine_id: int) -> RecallResult:
    """Tiered recall: return the best prior shot as a starting point.

    Tiers (first match wins):
      1 - exact combo, dialed-in
      2 - exact combo, any reason
      3 - (stub) approximate: same bean, same grinder+machine model, different unit
      4 - (stub) approximate: same bean, one dimension matches
      5 - generic defaults
    """
    base = (
        db.query(Shot)
        .filter(
            Shot.bean_id == bean_id,
            Shot.grinder_id == grinder_id,
            Shot.machine_id == machine_id,
        )
        .order_by(Shot.created_at.desc(), Shot.id.desc())
    )

    # Tier 1: exact combo + DIALED_IN
    dialed = base.filter(Shot.reason_code == ReasonCode.DIALED_IN).first()
    if dialed:
        return _result_from_shot(dialed, tier=1)

    # Tier 2: exact combo, any reason
    any_shot = base.first()
    if any_shot:
        return _result_from_shot(any_shot, tier=2)

    # TODO: Tier 3 - approximate: same bean, same grinder model + machine model,
    #       different physical unit, dialed-in. Requires joining on Grinder.brand/model
    #       and Machine.brand/model with exclusion of the exact IDs.

    # TODO: Tier 4 - approximate: same bean, one dimension matches.
    #       Broadest approximate search before falling back to generic.

    # Tier 5: generic defaults
    return _generic()
