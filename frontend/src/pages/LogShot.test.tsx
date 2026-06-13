import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { LogShot } from "./LogShot";
import { AuthProvider } from "@/contexts/AuthContext";

vi.mock("@/lib/api", () => ({
  fetchBeans: vi.fn().mockResolvedValue([
    { id: 1, brand: "Onyx", product: "Tropical Weather", notes: null },
  ]),
  fetchGrinders: vi.fn().mockResolvedValue([
    {
      id: 1,
      brand: "Niche",
      model: "Zero",
      label: null,
      scale_type: "STEPLESS",
      step_native: 8,
      finer_is_lower: true,
      snap: 5,
      min_native: null,
      max_native: null,
      unit_label: "°",
    },
  ]),
  fetchMachines: vi.fn().mockResolvedValue([
    {
      id: 1,
      brand: "Breville",
      model: "Bambino",
      label: null,
      notes: null,
    },
  ]),
  fetchPreferences: vi.fn().mockResolvedValue({
    grinder_id: null,
    machine_id: null,
  }),
  fetchRecall: vi.fn().mockResolvedValue({
    confidence_label: "GENERIC",
    source_tier: 5,
    grind_setting_native: null,
    dose_g: 18,
    yield_g: 36,
    time_s: 28,
    shot_id: null,
  }),
  createShot: vi.fn(),
  setOnUnauthorized: vi.fn(),
  setToken: vi.fn(),
  clearToken: vi.fn(),
}));

function setFakeAuth() {
  const token =
    "header." +
    btoa(JSON.stringify({ sub: "1", exp: Math.floor(Date.now() / 1000) + 3600 })) +
    ".sig";
  localStorage.setItem("koffeeza_token", token);
  localStorage.setItem(
    "koffeeza_user",
    JSON.stringify({ id: 1, name: "Test", has_pin: false }),
  );
}

async function renderLogShot() {
  setFakeAuth();
  await act(async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <LogShot />
        </AuthProvider>
      </MemoryRouter>,
    );
  });
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe("LogShot", () => {
  it("renders without crashing", async () => {
    await renderLogShot();
    expect(screen.getByText("Log a Shot")).toBeInTheDocument();
  });

  it("renders all five taste buttons", async () => {
    await renderLogShot();
    expect(screen.getByText("Sour")).toBeInTheDocument();
    expect(screen.getByText("Bitter")).toBeInTheDocument();
    expect(screen.getByText("Balanced")).toBeInTheDocument();
    expect(screen.getByText("Weak")).toBeInTheDocument();
    expect(screen.getByText("Astringent")).toBeInTheDocument();
  });

  it("allows selecting a taste", async () => {
    await renderLogShot();
    const sourButton = screen.getByText("Sour").closest("button")!;
    fireEvent.click(sourButton);
    expect(sourButton).toHaveClass("ring-2");
  });

  it("shows intensity options after selecting a non-balanced taste", async () => {
    await renderLogShot();
    fireEvent.click(screen.getByText("Sour"));
    expect(screen.getByText("Mild")).toBeInTheDocument();
    expect(screen.getByText("Strong")).toBeInTheDocument();
  });

  it("hides intensity options when balanced is selected", async () => {
    await renderLogShot();
    fireEvent.click(screen.getByText("Sour"));
    expect(screen.getByText("Mild")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Balanced"));
    expect(screen.queryByText("Mild")).not.toBeInTheDocument();
  });

  it("shows validation error when submitting empty form", async () => {
    await renderLogShot();
    fireEvent.click(screen.getByText("Log Shot"));
    expect(
      screen.getByText("Please select a bean, grinder, and machine."),
    ).toBeInTheDocument();
  });

  it("renders form fields for shot data", async () => {
    await renderLogShot();
    expect(screen.getByLabelText("Dose (g)")).toBeInTheDocument();
    expect(screen.getByLabelText("Yield (g)")).toBeInTheDocument();
    expect(screen.getByLabelText("Time (s)")).toBeInTheDocument();
    expect(screen.getByLabelText("Grind Setting")).toBeInTheDocument();
  });
});
