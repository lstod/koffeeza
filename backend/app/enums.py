import enum


class Taste(enum.StrEnum):
    SOUR = "SOUR"
    BITTER = "BITTER"
    BALANCED = "BALANCED"
    WEAK = "WEAK"
    ASTRINGENT = "ASTRINGENT"


class Intensity(enum.StrEnum):
    MILD = "MILD"
    STRONG = "STRONG"


class ScaleType(enum.StrEnum):
    STEPPED = "STEPPED"
    CLICKS = "CLICKS"
    STEPLESS = "STEPLESS"


class Direction(enum.StrEnum):
    FINER = "FINER"
    COARSER = "COARSER"
    NONE = "NONE"


class Confidence(enum.StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ReasonCode(enum.StrEnum):
    CHANNELING_SUSPECTED = "CHANNELING_SUSPECTED"
    FLOW_TOO_FAST = "FLOW_TOO_FAST"
    FLOW_TOO_SLOW = "FLOW_TOO_SLOW"
    FLOW_FAST = "FLOW_FAST"
    FLOW_SLOW = "FLOW_SLOW"
    DIALED_IN = "DIALED_IN"
    TASTE_SOUR = "TASTE_SOUR"
    TASTE_BITTER = "TASTE_BITTER"
    TASTE_WEAK = "TASTE_WEAK"
    TASTE_ASTRINGENT = "TASTE_ASTRINGENT"
