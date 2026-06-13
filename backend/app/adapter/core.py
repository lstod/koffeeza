from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.enums import Direction, ScaleType


@runtime_checkable
class GrinderLike(Protocol):
    scale_type: ScaleType
    step_native: float
    finer_is_lower: bool
    snap: float
    min_native: float | None
    max_native: float | None
    unit_label: str


@dataclass(frozen=True)
class Instruction:
    text: str
    direction: str | None
    relative: float | None
    target: float | None
    clamped: bool
    unit: str


_CLAMP_FINER_MSG = (
    "You're at the finest usable setting; if it's still too fast, "
    "the cause is likely dose or distribution, not grind."
)


def _snap_delta(raw_delta: float, snap: float) -> float:
    snapped = round(raw_delta / snap) * snap
    if snapped == 0:
        snapped = snap
    return snapped


def _clamp(value: float, lo: float | None, hi: float | None) -> tuple[float, bool]:
    clamped = False
    if lo is not None and value < lo:
        value = lo
        clamped = True
    if hi is not None and value > hi:
        value = hi
        clamped = True
    return value, clamped


def to_instruction(
    grinder: GrinderLike,
    current_native: float | None,
    direction: Direction,
    magnitude_normalized: float,
) -> Instruction:
    if direction == Direction.NONE:
        return Instruction(
            text="No change — dialed in.",
            direction=None,
            relative=None,
            target=None,
            clamped=False,
            unit=grinder.unit_label,
        )

    delta = _snap_delta(magnitude_normalized * grinder.step_native, grinder.snap)

    if grinder.scale_type == ScaleType.CLICKS:
        label = f"{direction.value.lower()} by {delta:g} {grinder.unit_label}".strip()
        return Instruction(
            text=f"Adjust {label}.",
            direction=direction.value,
            relative=delta,
            target=None,
            clamped=False,
            unit=grinder.unit_label,
        )

    # STEPPED / STEPLESS — compute absolute target
    if current_native is None:
        label = f"{direction.value.lower()} by {delta:g}"
        if grinder.unit_label:
            label += f" {grinder.unit_label}"
        return Instruction(
            text=f"Adjust {label}.",
            direction=direction.value,
            relative=delta,
            target=None,
            clamped=False,
            unit=grinder.unit_label,
        )

    going_finer = direction == Direction.FINER
    if grinder.finer_is_lower:
        target = current_native - delta if going_finer else current_native + delta
    else:
        target = current_native + delta if going_finer else current_native - delta

    target, clamped = _clamp(target, grinder.min_native, grinder.max_native)
    actual_delta = abs(target - current_native)

    parts: list[str] = []
    if going_finer:
        parts.append(f"Go finer to {target:g}")
    else:
        parts.append(f"Go coarser to {target:g}")
    if grinder.unit_label:
        parts[0] += f" {grinder.unit_label}"
    parts[0] += f" (move {actual_delta:g}"
    if grinder.unit_label:
        parts[0] += f" {grinder.unit_label}"
    parts[0] += f" {direction.value.lower()})."

    if clamped and going_finer:
        parts.append(_CLAMP_FINER_MSG)

    return Instruction(
        text=" ".join(parts),
        direction=direction.value,
        relative=actual_delta,
        target=target,
        clamped=clamped,
        unit=grinder.unit_label,
    )
