from __future__ import annotations

from typing import TYPE_CHECKING

from app.enums import ScaleType
from app.models.grinder import Grinder

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

SEED_GRINDERS: list[dict] = [
    {
        "brand": "(default)",
        "model": "—",
        "scale_type": ScaleType.STEPPED,
        "step_native": 1.0,
        "finer_is_lower": True,
        "snap": 1.0,
        "unit_label": "",
    },
    {
        "brand": "Niche",
        "model": "Zero",
        "scale_type": ScaleType.STEPLESS,
        "step_native": 8.0,
        "finer_is_lower": True,
        "snap": 5.0,
        "unit_label": "°",
    },
    {
        "brand": "Comandante",
        "model": "C40",
        "scale_type": ScaleType.CLICKS,
        "step_native": 2.0,
        "finer_is_lower": True,
        "snap": 1.0,
        "unit_label": "clicks",
    },
    {
        "brand": "Baratza",
        "model": "Encore",
        "scale_type": ScaleType.STEPPED,
        "step_native": 1.5,
        "finer_is_lower": True,
        "snap": 1.0,
        "unit_label": "",
    },
    {
        "brand": "Baratza",
        "model": "Sette 30",
        "scale_type": ScaleType.STEPPED,
        "step_native": 1.0,
        "finer_is_lower": True,
        "snap": 1.0,
        "min_native": 1.0,
        "max_native": 31.0,
        "unit_label": "",
    },
]


def seed_grinders(session: Session) -> int:
    """Insert seed grinder profiles if the table is empty. Returns count inserted."""
    if session.query(Grinder).count() > 0:
        return 0

    for data in SEED_GRINDERS:
        session.add(Grinder(**data))
    session.commit()
    return len(SEED_GRINDERS)
