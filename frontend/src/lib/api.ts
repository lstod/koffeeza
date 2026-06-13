import type {
  BeanCreate,
  BeanResponse,
  GrinderCreate,
  GrinderResponse,
  MachineCreate,
  MachineResponse,
  PreferenceResponse,
  RecallResponse,
  ShotCreate,
  ShotSuggestionResponse,
} from "./types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(body || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Beans ───────────────────────────────────────────────────────────────────

export function fetchBeans(): Promise<BeanResponse[]> {
  return request("/beans");
}

export function createBean(data: BeanCreate): Promise<BeanResponse> {
  return request("/beans", { method: "POST", body: JSON.stringify(data) });
}

// ── Grinders ────────────────────────────────────────────────────────────────

export function fetchGrinders(): Promise<GrinderResponse[]> {
  return request("/grinders");
}

export function createGrinder(data: GrinderCreate): Promise<GrinderResponse> {
  return request("/grinders", { method: "POST", body: JSON.stringify(data) });
}

// ── Machines ────────────────────────────────────────────────────────────────

export function fetchMachines(): Promise<MachineResponse[]> {
  return request("/machines");
}

export function createMachine(data: MachineCreate): Promise<MachineResponse> {
  return request("/machines", { method: "POST", body: JSON.stringify(data) });
}

// ── Recall ──────────────────────────────────────────────────────────────────

export function fetchRecall(
  beanId: number,
  grinderId: number,
  machineId: number,
): Promise<RecallResponse> {
  const params = new URLSearchParams({
    bean_id: String(beanId),
    grinder_id: String(grinderId),
    machine_id: String(machineId),
  });
  return request(`/recall?${params}`);
}

// ── Shots ───────────────────────────────────────────────────────────────────

export function createShot(
  data: ShotCreate,
): Promise<ShotSuggestionResponse> {
  return request("/shots", { method: "POST", body: JSON.stringify(data) });
}

// ── Preferences ─────────────────────────────────────────────────────────────

export function fetchPreferences(): Promise<PreferenceResponse> {
  return request("/preferences");
}
