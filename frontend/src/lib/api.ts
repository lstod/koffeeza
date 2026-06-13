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
  ShotResponse,
  ShotSuggestionResponse,
  UserLoginResponse,
  UserResponse,
} from "./types";

const BASE = "/api";
const TOKEN_KEY = "koffeeza_token";

let onUnauthorized: (() => void) | null = null;

export function setOnUnauthorized(cb: () => void) {
  onUnauthorized = cb;
}

function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, { headers, ...init });

  if (res.status === 401 || res.status === 403) {
    clearToken();
    onUnauthorized?.();
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(body || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── Users (no auth required) ────────────────────────────────────────────────

export function fetchUsers(): Promise<UserResponse[]> {
  return request("/users");
}

export function createUser(
  name: string,
  pin?: string,
): Promise<UserLoginResponse> {
  return request("/users", {
    method: "POST",
    body: JSON.stringify({ name, pin: pin || null }),
  });
}

export function loginUser(
  userId: number,
  pin?: string,
): Promise<UserLoginResponse> {
  return request(`/users/${userId}/login`, {
    method: "POST",
    body: JSON.stringify({ pin: pin || null }),
  });
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

export function fetchShots(beanId?: number): Promise<ShotResponse[]> {
  const params = beanId != null ? `?bean_id=${beanId}` : "";
  return request(`/shots${params}`);
}

export function createShot(
  data: ShotCreate,
): Promise<ShotSuggestionResponse> {
  return request("/shots", { method: "POST", body: JSON.stringify(data) });
}

// ── Preferences ─────────────────────────────────────────────────────────────

export function fetchPreferences(): Promise<PreferenceResponse> {
  return request("/preferences");
}
