import { render, screen } from "@testing-library/react";
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
  it("renders the LogShot page at /", () => {
    render(<App />);
    expect(screen.getByText("Log a Shot")).toBeInTheDocument();
  });

  it("renders the bottom navigation bar", () => {
    render(<App />);
    const nav = screen.getByRole("navigation");
    expect(nav).toBeInTheDocument();
    expect(nav).toHaveTextContent("Log");
    expect(nav).toHaveTextContent("Setup");
  });
});
