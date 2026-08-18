

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence


# ---------------------------------------------------------------------------
# Indicator definitions
# ---------------------------------------------------------------------------

class Indicator(str, Enum):
    """The ten things measured. The string values are the API and DB keys."""

    ACTIVE_USERS = "users"
    USAGE_FREQUENCY = "freq"
    TRAINING = "train"
    WORKFLOW = "flow"
    TASK_VOLUME = "tasks"
    WORKFLOW_COVERAGE = "cover"
    PROFICIENCY = "prof"
    SAFE_USE = "comp"
    AGENT_CREATION = "agent"
    PROCESS_AUTOMATION = "automate"
    


INDICATOR_LABELS: Dict[Indicator, str] = {
    Indicator.ACTIVE_USERS: "Active AI users",
    Indicator.USAGE_FREQUENCY: "Usage frequency",
    Indicator.TRAINING: "Training completion",
    Indicator.WORKFLOW: "AI in weekly workflow",
    Indicator.TASK_VOLUME: "AI-assisted task volume",
    Indicator.WORKFLOW_COVERAGE: "Eligible workflows covered",
    Indicator.PROFICIENCY: "Proficiency and readiness",
    Indicator.SAFE_USE: "Safe use of AI",
    Indicator.AGENT_CREATION: "AI agents built",
    Indicator.PROCESS_AUTOMATION: "Processes automated",
}

DEFAULT_WEIGHTS: Dict[str, float] = {
    Indicator.ACTIVE_USERS: 16,
    Indicator.USAGE_FREQUENCY: 15,
    Indicator.TRAINING: 15,
    Indicator.WORKFLOW: 15,
    Indicator.TASK_VOLUME: 8,
    Indicator.WORKFLOW_COVERAGE: 10,
    Indicator.PROFICIENCY: 10,
    Indicator.SAFE_USE: 5,
    Indicator.AGENT_CREATION: 3,
    Indicator.PROCESS_AUTOMATION: 3,
}

# Targets that define a score of 100 for indicators measured in natural units.
SESSIONS_PER_WEEK_TARGET = 5.0
TASKS_PER_MONTH_TARGET = 20.0


# ---------------------------------------------------------------------------
# Maturity bands
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Band:
    name: str
    low: int
    high: int
    description: str


BANDS: Sequence[Band] = (
    Band("Emerging", 0, 25, "Aware, little real use"),
    Band("Developing", 26, 50, "Pockets of use, no routine"),
    Band("Established", 51, 75, "Routine use by most"),
    Band("Advanced", 76, 90, "Embedded in core workflows"),
    Band("Leading", 91, 100, "Sets the practice for others"),
)


def band_for(rate: float) -> Band:
    """The maturity band a given adoption rate falls into."""
    for band in reversed(BANDS):
        if rate >= band.low:
            return band
    return BANDS[0]


# ---------------------------------------------------------------------------
# Employee level adjustments
# ---------------------------------------------------------------------------

class Level(str, Enum):
    ALL = "all"
    LEADERSHIP = "leadership"
    MANAGER = "manager"
    SPECIALIST = "specialist"
    SUPPORT = "support"


# Seniority correlates with AI use, so viewing the dashboard filtered to one
# level shifts the behavioural indicators. Structural indicators such as
# training completion are not adjusted, because they are counted, not estimated.
LEVEL_ADJUSTMENT: Dict[Level, float] = {
    Level.ALL: 0.0,
    Level.LEADERSHIP: 7.0,
    Level.MANAGER: 3.0,
    Level.SPECIALIST: 0.0,
    Level.SUPPORT: -11.0,
}

LEVEL_SENSITIVE = {
    Indicator.ACTIVE_USERS,
    Indicator.USAGE_FREQUENCY,
    Indicator.WORKFLOW,
    Indicator.PROFICIENCY,
}


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Keep a score inside 0-100. Adjustments can push a value past either end."""
    return max(low, min(high, float(value)))


def scale_to_target(observed: float, target: float) -> float:
    """
    Convert a natural unit into a 0-100 score against the value that counts as
    full marks. Six sessions a week against a target of five is 100, not 120:
    exceeding the target is good but should not mask a weakness elsewhere.
    """
    if target <= 0:
        raise ValueError("target must be positive")
    return clamp(observed / target * 100.0)


def normalise_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Scale weights so they sum to 100. Leadership adjusting one slider should not
    silently change the meaning of every other indicator, and a set summing to
    87 or 113 should still produce a usable score.
    """
    total = sum(max(0.0, float(w)) for w in weights.values())
    if total <= 0:
        raise ValueError("at least one weight must be greater than zero")
    return {k: max(0.0, float(v)) / total * 100.0 for k, v in weights.items()}


# ---------------------------------------------------------------------------
# Indicator scores for one department in one wave
# ---------------------------------------------------------------------------

@dataclass
class IndicatorScores:

    users: float = 0.0
    freq: float = 0.0
    train: float = 0.0
    flow: float = 0.0
    tasks: float = 0.0
    cover: float = 0.0
    prof: float = 0.0
    comp: float = 0.0
    agent: float = 0.0
    automate: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            Indicator.ACTIVE_USERS: self.users,
            Indicator.USAGE_FREQUENCY: self.freq,
            Indicator.TRAINING: self.train,
            Indicator.WORKFLOW: self.flow,
            Indicator.TASK_VOLUME: self.tasks,
            Indicator.WORKFLOW_COVERAGE: self.cover,
            Indicator.PROFICIENCY: self.prof,
            Indicator.SAFE_USE: self.comp,
            Indicator.AGENT_CREATION: self.agent,
            Indicator.PROCESS_AUTOMATION: self.automate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "IndicatorScores":
        return cls(**{k: clamp(v) for k, v in data.items() if k in cls.__annotations__})


def adjusted_scores(scores: IndicatorScores, level: Level = Level.ALL) -> Dict[str, float]:
    """Apply the employee level adjustment to the behavioural indicators only."""
    delta = LEVEL_ADJUSTMENT.get(level, 0.0)
    out: Dict[str, float] = {}
    for key, value in scores.as_dict().items():
        shift = delta if Indicator(key) in LEVEL_SENSITIVE else 0.0
        out[key] = clamp(value + shift)
    return out


def adoption_rate(
    scores: IndicatorScores,
    weights: Optional[Dict[str, float]] = None,
    level: Level = Level.ALL,
) -> float:
    """
    The headline number: a weighted mean of the eight indicator scores.

    Because the weights are normalised first, this is a true weighted average
    and always lands between 0 and 100 without needing to be clamped.
    """
    weights = normalise_weights(weights or DEFAULT_WEIGHTS)
    values = adjusted_scores(scores, level)
    total = sum(values[k] * weights.get(k, 0.0) for k in values)
    return round(total / 100.0, 2)


# ---------------------------------------------------------------------------
# Organisation level roll-up
# ---------------------------------------------------------------------------

@dataclass
class DepartmentResult:
    """One department's outcome for one wave, ready to serialise."""

    name: str
    function: str = "Unassigned"
    headcount: int = 0
    respondents: int = 0
    active_users: int = 0
    scores: IndicatorScores = field(default_factory=IndicatorScores)
    sessions_per_week: float = 0.0
    use_cases: int = 0
    tools: List[List] = field(default_factory=list)
    processes: List[str] = field(default_factory=list)
    gap: str = "Not recorded"
    opportunity: str = "Not recorded"
    ai_solutions: int = 0
    ai_solutions_personal: int = 0

    @property
    def response_rate(self) -> float:
        if self.headcount <= 0:
            return 0.0
        return round(self.respondents / self.headcount * 100.0, 1)

    def reliability(self) -> str:
        """
        With no system data behind the numbers, a department's score is only as
        trustworthy as the share of its people who answered. Part K of the survey
        sets these thresholds; they are enforced here so the API can never
        present a thin sample as a solid result.
        """
        rate = self.response_rate
        if rate >= 60:
            return "reliable"
        if rate >= 40:
            return "provisional"
        return "insufficient"


def organisation_rate(
    results: Iterable[DepartmentResult],
    weights: Optional[Dict[str, float]] = None,
    level: Level = Level.ALL,
) -> Optional[float]:
    """
    Employee-weighted mean across departments.

    Weighting by headcount rather than taking a simple average matters: a
    9-person team at 82% and a 41-person team at 36% is not a 59% organisation.
    An unweighted average would let small enthusiastic teams hide the fact that
    most of the company is not using AI.
    """
    numerator = 0.0
    denominator = 0
    for result in results:
        if result.headcount <= 0:
            continue
        numerator += adoption_rate(result.scores, weights, level) * result.headcount
        denominator += result.headcount
    if denominator == 0:
        return None
    return round(numerator / denominator, 2)


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

class TargetStatus(str, Enum):
    ABOVE = "above"
    ON_TRACK = "on_track"
    BELOW = "below"
    CRITICAL = "critical"


ON_TRACK_TOLERANCE = 10.0


def target_status(rate: float, target: float, minimum: float) -> TargetStatus:
    """Four states, so a department that is merely behind is not confused with one that is a risk."""
    if rate < minimum:
        return TargetStatus.CRITICAL
    if rate >= target:
        return TargetStatus.ABOVE
    if rate >= target - ON_TRACK_TOLERANCE:
        return TargetStatus.ON_TRACK
    return TargetStatus.BELOW


# ---------------------------------------------------------------------------
# Wave comparison
# ---------------------------------------------------------------------------

@dataclass
class Movement:
    """Change in one department between two waves."""

    name: str
    before: Optional[float]
    after: Optional[float]

    @property
    def delta(self) -> Optional[float]:
        if self.before is None or self.after is None:
            return None
        return round(self.after - self.before, 2)


def compare_waves(
    before: Sequence[DepartmentResult],
    after: Sequence[DepartmentResult],
    weights: Optional[Dict[str, float]] = None,
) -> List[Movement]:
    """
    Match departments by name across two waves.

    A department present in only one wave returns None on that side rather than
    zero. Zero would read as "adoption collapsed to nothing" when the truth is
    "we did not measure it", and that distinction is the whole point of running
    the survey twice.
    """
    before_by_name = {d.name: d for d in before}
    after_by_name = {d.name: d for d in after}
    names = sorted(set(before_by_name) | set(after_by_name))

    movements: List[Movement] = []
    for name in names:
        b = before_by_name.get(name)
        a = after_by_name.get(name)
        movements.append(
            Movement(
                name=name,
                before=adoption_rate(b.scores, weights) if b else None,
                after=adoption_rate(a.scores, weights) if a else None,
            )
        )
    return movements
