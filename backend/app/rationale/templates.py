from app.enums import ReasonCode

TEMPLATES: dict[str, str] = {
    ReasonCode.FLOW_TOO_FAST: (
        "Your shot ran in {time_s}s — way too fast for the"
        " {t_lo}-{t_hi}s window. Grind significantly finer."
    ),
    ReasonCode.FLOW_FAST: (
        "Your shot ran in {time_s}s, a bit faster than the"
        " {t_lo}-{t_hi}s window. Grind a touch finer to slow extraction."
    ),
    ReasonCode.FLOW_TOO_SLOW: (
        "Your shot took {time_s}s — much too slow. Grind coarser. Also check puck prep."
    ),
    ReasonCode.FLOW_SLOW: (
        "Your shot took {time_s}s, a bit over the {t_lo}-{t_hi}s window. Grind slightly coarser."
    ),
    ReasonCode.DIALED_IN: (
        "{time_s}s and balanced — this one's dialed in. Saved as your starting point for this bean."
    ),
    ReasonCode.TASTE_SOUR: (
        "Timing looks good at {time_s}s but the shot tastes sour."
        " Grind a little finer for more extraction."
    ),
    ReasonCode.TASTE_BITTER: (
        "Timing is fine at {time_s}s but it's tasting bitter."
        " Grind slightly coarser to reduce extraction."
    ),
    ReasonCode.TASTE_WEAK: (
        "Shot timing is OK but the cup is weak."
        " Try grinding finer, or tighten the ratio for more intensity."
    ),
    ReasonCode.TASTE_ASTRINGENT: (
        "Astringency often signals channeling — check distribution"
        " and tamp first. If puck prep is good, grind slightly coarser."
    ),
    ReasonCode.CHANNELING_SUSPECTED: (
        "Flow and taste disagree, which usually means uneven extraction"
        " rather than grind. Re-distribute and tamp level, then pull"
        " again before changing grind."
    ),
}


def render_rationale(reason_code: str, facts: dict) -> str:
    template = TEMPLATES[reason_code]
    return template.format_map(facts)
