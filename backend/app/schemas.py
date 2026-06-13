from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.enums import Intensity, ScaleType, Taste

# ── User ─────────────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    name: str
    pin: str | None = None


class UserLogin(BaseModel):
    pin: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    has_pin: bool = False

    @model_validator(mode="before")
    @classmethod
    def _compute_has_pin(cls, data):
        if hasattr(data, "pin_hash"):
            return {
                "id": data.id,
                "name": data.name,
                "has_pin": data.pin_hash is not None,
            }
        return data


class UserLoginResponse(BaseModel):
    user: UserResponse
    token: str


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
    taste: Taste | None = None
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
    taste: Taste | None
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
    rationale_source: str = "template"


# ── Recall ──────────────────────────────────────────────────────────────────


class RecallResponse(BaseModel):
    confidence_label: str
    source_tier: int
    grind_setting_native: str | None
    dose_g: float
    yield_g: float
    time_s: float
    shot_id: int | None


# ── Preferences ─────────────────────────────────────────────────────────────


class PreferenceUpdate(BaseModel):
    grinder_id: int | None = None
    machine_id: int | None = None


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    grinder_id: int | None
    machine_id: int | None
