import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App";

vi.mock("@/lib/api", () => ({
  fetchBeans: vi.fn().mockResolvedValue([]),
  fetchGrinders: vi.fn().mockResolvedValue([]),
  fetchMachines: vi.fn().mockResolvedValue([]),
  fetchPreferences: vi
    .fn()
    .mockResolvedValue({ grinder_id: null, machine_id: null }),
  fetchUsers: vi.fn().mockResolvedValue([]),
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

beforeEach(() => {
  localStorage.clear();
});

describe("App", () => {
  it("renders onboarding when no equipment is configured", async () => {
    setFakeAuth();
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByText("Welcome to Koffeeza")).toBeInTheDocument();
  });

  it("renders the bottom navigation bar", async () => {
    setFakeAuth();
    await act(async () => {
      render(<App />);
    });
    const nav = screen.getByRole("navigation");
    expect(nav).toBeInTheDocument();
    expect(nav).toHaveTextContent("Log");
    expect(nav).toHaveTextContent("History");
    expect(nav).toHaveTextContent("Setup");
  });

  it("shows user picker when not authenticated", async () => {
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByText("Koffeeza")).toBeInTheDocument();
    expect(screen.getByText("Create Profile")).toBeInTheDocument();
  });
});
