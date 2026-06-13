from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.enums import Intensity, ScaleType, Taste

# ── Bean ─────────────────────────────────────────────────────────────────────


class BeanCreate(BaseModel):
    brand: str
    product: str
    notes: str | None = None


class BeanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    product: str
    notes: str | None


# ── Grinder ──────────────────────────────────────────────────────────────────


class GrinderCreate(BaseModel):
    brand: str
    model: str
    label: str | None = None
    scale_type: ScaleType
    step_native: float
    finer_is_lower: bool
    snap: float
    min_native: float | None = None
    max_native: float | None = None
    unit_label: str


class GrinderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    label: str | None
    scale_type: ScaleType
    step_native: float
    finer_is_lower: bool
    snap: float
    min_native: float | None
    max_native: float | None
    unit_label: str


# ── Machine ──────────────────────────────────────────────────────────────────


class MachineCreate(BaseModel):
    brand: str
    model: str
    label: str | None = None
    notes: str | None = None


class MachineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    label: str | None
    notes: str | None


# ── Shot ─────────────────────────────────────────────────────────────────────


class ShotCreate(BaseModel):
    bean_id: int
    grinder_id: int
    machine_id: int
    grind_setting_native: str
    dose_g: float
    yield_g: float
    time_s: float
    taste: Taste
    intensity: Intensity | None = None
    roast_date: date | None = None


class ShotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bean_id: int
    grinder_id: int
    machine_id: int
    grind_setting_native: str
    dose_g: float
    yield_g: float
    time_s: float
    taste: Taste
    intensity: Intensity | None
    reason_code: str
    roast_date: date | None
    created_at: datetime


class ShotSuggestionResponse(BaseModel):
    shot: ShotResponse
    direction: str | None
    magnitude_normalized: float
    confidence: str
    instruction: str
    rationale: str
