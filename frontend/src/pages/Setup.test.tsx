import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { Setup } from "./Setup";

vi.mock("@/lib/api", () => ({
  fetchBeans: vi.fn().mockResolvedValue([]),
  fetchGrinders: vi.fn().mockResolvedValue([]),
  fetchMachines: vi.fn().mockResolvedValue([]),
  createBean: vi.fn(),
  createGrinder: vi.fn(),
  createMachine: vi.fn(),
}));

async function renderSetup() {
  await act(async () => {
    render(
      <MemoryRouter>
        <Setup />
      </MemoryRouter>,
    );
  });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("Setup", () => {
  it("renders without crashing", async () => {
    await renderSetup();
    expect(screen.getByText("Setup")).toBeInTheDocument();
  });

  it("renders all three tabs", async () => {
    await renderSetup();
    expect(screen.getByRole("tab", { name: "Beans" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Grinders" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Machines" })).toBeInTheDocument();
  });

  it("shows beans tab by default with add button", async () => {
    await renderSetup();
    expect(screen.getByText("Add Bean")).toBeInTheDocument();
  });

  it("shows empty state message for beans", async () => {
    await renderSetup();
    expect(screen.getByText(/No beans added yet/)).toBeInTheDocument();
  });
});
