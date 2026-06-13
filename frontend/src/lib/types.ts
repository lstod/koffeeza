// ── User ────────────────────────────────────────────────────────────────────

export interface UserResponse {
  id: number;
  name: string;
  has_pin: boolean;
}

export interface UserLoginResponse {
  user: UserResponse;
  token: string;
}

// ── Enums ───────────────────────────────────────────────────────────────────

export type Taste = "SOUR" | "BITTER" | "BALANCED" | "WEAK" | "ASTRINGENT";
export type Intensity = "MILD" | "STRONG";
export type ScaleType = "STEPPED" | "CLICKS" | "STEPLESS";

export const TASTE_OPTIONS: Taste[] = [
  "SOUR",
  "BITTER",
  "BALANCED",
  "WEAK",
  "ASTRINGENT",
];

export const INTENSITY_OPTIONS: Intensity[] = ["MILD", "STRONG"];

export const SCALE_TYPE_OPTIONS: ScaleType[] = [
  "STEPPED",
  "CLICKS",
  "STEPLESS",
];

// ── Bean ────────────────────────────────────────────────────────────────────

export interface BeanCreate {
  brand: string;
  product: string;
  notes: string | null;
}

export interface BeanResponse {
  id: number;
  brand: string;
  product: string;
  notes: string | null;
}

// ── Grinder ─────────────────────────────────────────────────────────────────

export interface GrinderCreate {
  brand: string;
  model: string;
  label: string | null;
  scale_type: ScaleType;
  step_native: number;
  finer_is_lower: boolean;
  snap: number;
  min_native: number | null;
  max_native: number | null;
  unit_label: string;
}

export interface GrinderResponse {
  id: number;
  brand: string;
  model: string;
  label: string | null;
  scale_type: ScaleType;
  step_native: number;
  finer_is_lower: boolean;
  snap: number;
  min_native: number | null;
  max_native: number | null;
  unit_label: string;
}

// ── Machine ─────────────────────────────────────────────────────────────────

export interface MachineCreate {
  brand: string;
  model: string;
  label: string | null;
  notes: string | null;
}

export interface MachineResponse {
  id: number;
  brand: string;
  model: string;
  label: string | null;
  notes: string | null;
}

// ── Shot ────────────────────────────────────────────────────────────────────

export interface ShotCreate {
  bean_id: number;
  grinder_id: number;
  machine_id: number;
  grind_setting_native: string;
  dose_g: number;
  yield_g: number;
  time_s: number;
  taste: Taste | null;
  intensity: Intensity | null;
  roast_date: string | null;
}

export interface ShotResponse {
  id: number;
  bean_id: number;
  grinder_id: number;
  machine_id: number;
  grind_setting_native: string;
  dose_g: number;
  yield_g: number;
  time_s: number;
  taste: Taste | null;
  intensity: Intensity | null;
  reason_code: string;
  roast_date: string | null;
  created_at: string;
}

export interface ShotSuggestionResponse {
  shot: ShotResponse;
  direction: string | null;
  magnitude_normalized: number;
  confidence: string;
  instruction: string;
  rationale: string;
  rationale_source: string;
}

// ── Recall ──────────────────────────────────────────────────────────────────

export interface RecallResponse {
  confidence_label: string;
  source_tier: number;
  grind_setting_native: string | null;
  dose_g: number;
  yield_g: number;
  time_s: number;
  shot_id: number | null;
}

// ── Preferences ─────────────────────────────────────────────────────────────

export interface PreferenceResponse {
  grinder_id: number | null;
  machine_id: number | null;
}
