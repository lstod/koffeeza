import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { Suggestion } from "./Suggestion";
import type { ShotSuggestionResponse } from "@/lib/types";

const baseSuggestion: ShotSuggestionResponse = {
  shot: {
    id: 1,
    bean_id: 1,
    grinder_id: 1,
    machine_id: 1,
    grind_setting_native: "12",
    dose_g: 18,
    yield_g: 36,
    time_s: 22,
    taste: "SOUR",
    intensity: null,
    reason_code: "FLOW_FAST",
    roast_date: null,
    created_at: "2026-01-01T00:00:00",
  },
  direction: "FINER",
  magnitude_normalized: 1.0,
  confidence: "MEDIUM",
  instruction: "Grind 1 step finer: 12 → 11",
  rationale:
    "Your shot ran in 22s, a bit faster than the 25-32s window. Grind a touch finer to slow extraction.",
  rationale_source: "template",
};

function renderSuggestion(suggestion?: ShotSuggestionResponse) {
  return render(
    <MemoryRouter
      initialEntries={[
        {
          pathname: "/suggestion",
          state: suggestion ? { suggestion } : undefined,
        },
      ]}
    >
      <Routes>
        <Route path="/" element={<div data-testid="home">Home</div>} />
        <Route path="/suggestion" element={<Suggestion />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("Suggestion", () => {
  it("renders instruction and rationale", () => {
    renderSuggestion(baseSuggestion);
    expect(screen.getByText(baseSuggestion.instruction)).toBeInTheDocument();
    expect(screen.getByText(baseSuggestion.rationale)).toBeInTheDocument();
  });

  it("displays confidence badge", () => {
    renderSuggestion(baseSuggestion);
    expect(
      screen.getByText("MEDIUM confidence"),
    ).toBeInTheDocument();
  });

  it("shows a dialed-in state when direction is null", () => {
    const dialedIn: ShotSuggestionResponse = {
      ...baseSuggestion,
      direction: null,
      magnitude_normalized: 0,
      confidence: "HIGH",
      instruction: "No change — dialed in.",
      rationale:
        "28s and balanced — this one's dialed in. Saved as your starting point for this bean.",
    };
    renderSuggestion(dialedIn);
    expect(screen.getByText("Dialed In!")).toBeInTheDocument();
    expect(screen.getByText(dialedIn.rationale)).toBeInTheDocument();
  });

  it("shows log another shot button", () => {
    renderSuggestion(baseSuggestion);
    expect(
      screen.getByRole("button", { name: "Log another shot" }),
    ).toBeInTheDocument();
  });

  it("redirects to / when no state is passed", () => {
    renderSuggestion(undefined);
    expect(screen.getByTestId("home")).toBeInTheDocument();
    expect(screen.queryByText("Dialed In!")).not.toBeInTheDocument();
  });
});
