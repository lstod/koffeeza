import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { History } from "./History";

vi.mock("@/lib/api", () => ({
  fetchShots: vi.fn().mockResolvedValue([
    {
      id: 1,
      bean_id: 1,
      grinder_id: 1,
      machine_id: 1,
      grind_setting_native: "12",
      dose_g: 18,
      yield_g: 36,
      time_s: 28,
      taste: "BALANCED",
      intensity: null,
      reason_code: "DIALED_IN",
      roast_date: null,
      created_at: "2026-06-13T10:00:00",
    },
    {
      id: 2,
      bean_id: 1,
      grinder_id: 1,
      machine_id: 1,
      grind_setting_native: "13",
      dose_g: 18,
      yield_g: 36,
      time_s: 22,
      taste: null,
      intensity: null,
      reason_code: "FLOW_FAST",
      roast_date: null,
      created_at: "2026-06-13T09:00:00",
    },
  ]),
  fetchBeans: vi.fn().mockResolvedValue([
    { id: 1, brand: "Onyx", product: "Tropical Weather", notes: null },
  ]),
}));

async function renderHistory() {
  await act(async () => {
    render(
      <MemoryRouter>
        <History />
      </MemoryRouter>,
    );
  });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("History", () => {
  it("renders without crashing", async () => {
    await renderHistory();
    expect(screen.getByText("Shot History")).toBeInTheDocument();
  });

  it("displays shot cards with bean name", async () => {
    await renderHistory();
    const cards = screen.getAllByText("Onyx — Tropical Weather");
    expect(cards.length).toBe(2);
  });

  it("shows reason badges", async () => {
    await renderHistory();
    expect(screen.getByText("Dialed in")).toBeInTheDocument();
    expect(screen.getByText("Running fast")).toBeInTheDocument();
  });

  it("shows shot parameters", async () => {
    await renderHistory();
    expect(screen.getAllByText("18g").length).toBeGreaterThan(0);
    expect(screen.getAllByText("36g").length).toBeGreaterThan(0);
  });

  it("handles shot with null taste", async () => {
    await renderHistory();
    const tasteElements = screen.queryAllByText(/^Taste:/);
    expect(tasteElements.length).toBe(1);
  });
});
