import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import App from "./App";

vi.mock("@/lib/api", () => ({
  fetchBeans: vi.fn().mockResolvedValue([]),
  fetchGrinders: vi.fn().mockResolvedValue([]),
  fetchMachines: vi.fn().mockResolvedValue([]),
  fetchPreferences: vi
    .fn()
    .mockResolvedValue({ grinder_id: null, machine_id: null }),
}));

describe("App", () => {
  it("renders onboarding when no equipment is configured", async () => {
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByText("Welcome to Koffeeza")).toBeInTheDocument();
  });

  it("renders the bottom navigation bar", async () => {
    await act(async () => {
      render(<App />);
    });
    const nav = screen.getByRole("navigation");
    expect(nav).toBeInTheDocument();
    expect(nav).toHaveTextContent("Log");
    expect(nav).toHaveTextContent("History");
    expect(nav).toHaveTextContent("Setup");
  });
});
