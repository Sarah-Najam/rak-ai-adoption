"""
Turning a raw survey export into scored departments.

This is the messy part of the system, and the part most likely to break, because
it is the only place that touches data produced by humans rather than by code.
Three things make it fragile, and each is handled deliberately.

**Column headings move.** Microsoft Forms exports the full question text as the
heading. Somebody fixes a typo between waves and an exact-match lookup breaks.
So columns are resolved by looking for a few distinctive words instead.

**Answers are free text, not codes.** "Most days" has to become 88. The mappings
live in tables at the top of this file rather than buried in the logic, so the
scoring rules can be read and checked by someone who does not write Python.

**People skip questions.** Every conversion has a defined behaviour for a blank,
and non-users are scored zero on usage indicators rather than dropped. Dropping
them would make a department with three keen users look fully adopted.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

from app.services.scoring import (
    DepartmentResult,
    IndicatorScores,
    scale_to_target,
    SESSIONS_PER_WEEK_TARGET,
    TASKS_PER_MONTH_TARGET,
)


# ---------------------------------------------------------------------------
# Locating columns
# ---------------------------------------------------------------------------

# Distinctive phrases, lowercase. First match wins, so order matters where two
# questions share wording. Add alternatives when the survey is reworded.
COLUMN_HINTS: Dict[str, Sequence[str]] = {
    "department": ("which department do you work in",),
    "level": ("which best describes your level",),
    "used_30d": ("used any ai tool for work in the last 30",),
    "tools": ("which of these have you used for work in the last 30",),
    "top_tool": ("which one do you use most",),
    "days": ("on how many days do you use ai",),
    "times": ("how many separate times",),
    "workflow": ("how often is ai part of how you do your job",),
    "regular_tasks": ("which of these do you use ai for regularly",),
    "task_count": ("how many work tasks did ai help you with",),
    "coverage": ("what share of them do you now use ai for",),
    "blockers": ("what stops you using ai more",),
    "account": ("which account do you normally use",),
    "pasted": ("have you put any of these into a personal ai account",),
    "training": ("have you completed any ai training",),
    "linking_code": ("personal code", "create your code"),
}

# Free-text idea boxes at E2. Any column matching these contributes.
IDEA_HINTS = ("name up to three tasks", "task 1", "task 2", "task 3")

# Part F. The key is the question label, the value is a phrase unique to the
# correct option. Matching on a phrase rather than the full option text means
# small edits to an answer do not silently mark everyone wrong.
KNOWLEDGE_ANSWERS: Dict[str, str] = {
    "F1": "deciding which contractor",
    "F2": "write a short email to a buyer",
    "F3": "you did not tell it who it is for",
    "F4": "known behavio",           # covers behaviour and behavior
    "F5": "producing a first draft",
    "F6": "give it two or three examples",
    "F7": "customer's name",
    "F8": "tell it what is wrong",
    "F9": "trained on information up to a point in time",
    "F10": "you, the person who sent the report",
}


def normalise(text: Any) -> str:
    """Collapse whitespace and lowercase, so matching survives formatting noise."""
    return re.sub(r"\s+", " ", str(text if text is not None else "")).strip().lower()


def find_column(columns: Iterable[str], hints: Sequence[str]) -> Optional[str]:
    for column in columns:
        heading = normalise(column)
        if any(hint in heading for hint in hints):
            return column
    return None


@dataclass
class ColumnMap:
    """Which spreadsheet column answers which question."""

    columns: Dict[str, Optional[str]]
    knowledge: Dict[str, Optional[str]]
    ideas: List[str]

    def get(self, key: str, row: Dict[str, Any]) -> Any:
        column = self.columns.get(key)
        return row.get(column) if column else None

    @property
    def missing(self) -> List[str]:
        return [k for k, v in self.columns.items() if v is None]


def map_columns(frame: pd.DataFrame) -> ColumnMap:
    columns = {key: find_column(frame.columns, hints) for key, hints in COLUMN_HINTS.items()}

    knowledge: Dict[str, Optional[str]] = {}
    for label in KNOWLEDGE_ANSWERS:
        # "F1." and "F1:" both appear in the wild; a bare "F1" would also match
        # any column containing that pair of characters, so require a separator.
        knowledge[label] = find_column(frame.columns, (label.lower() + ".", label.lower() + ":"))

    ideas = [c for c in frame.columns if any(h in normalise(c) for h in IDEA_HINTS)]

    return ColumnMap(columns=columns, knowledge=knowledge, ideas=ideas)


# ---------------------------------------------------------------------------
# Answer to number
# ---------------------------------------------------------------------------

# Longest phrases first where one contains another, since first match wins.
WORKFLOW_POINTS: Sequence[Tuple[str, float]] = (
    ("every working day", 100),
    ("most days", 88),
    ("several times a week", 70),
    ("about once a week", 45),
    ("rarely", 20),
    ("never", 0),
)

COVERAGE_POINTS: Sequence[Tuple[str, float]] = (
    ("almost all", 100),
    ("more than three quarters", 85),
    ("half to three quarters", 63),
    ("quarter to a half", 38),
    ("under a quarter", 15),
    ("none of them", 0),
)

DAYS_PER_WEEK: Sequence[Tuple[str, float]] = (
    ("5 or more", 5.0),
    ("4 day", 4.0),
    ("3 day", 3.0),
    ("2 day", 2.0),
    ("less than one", 0.5),
    ("1 day", 1.0),
)

TIMES_PER_DAY: Sequence[Tuple[str, float]] = (
    ("more than 10", 12.0),
    ("7 to 10", 8.5),
    ("4 to 6", 5.0),
    ("2 to 3", 2.5),
    ("once", 1.0),
)

TASKS_PER_MONTH: Sequence[Tuple[str, float]] = (
    ("more than 60", 75.0),
    ("31 to 60", 45.0),
    ("16 to 30", 23.0),
    ("6 to 15", 10.0),
    ("1 to 5", 3.0),
    ("none", 0.0),
)

ACCOUNT_PENALTY: Sequence[Tuple[str, float]] = (
    ("always a personal", 40),
    ("mostly a personal", 25),
    ("about half and half", 15),
    ("did not know the company provides", 20),
)

SENSITIVE_CATEGORY_PENALTY = 12.0
PREFER_NOT_TO_SAY_PENALTY = 12.0


def lookup(value: Any, table: Sequence[Tuple[str, float]], default: float = 0.0) -> float:
    """First phrase in the table that appears in the answer wins."""
    answer = normalise(value)
    if not answer:
        return default
    for phrase, points in table:
        if phrase in answer:
            return float(points)
    return default


def is_yes(value: Any) -> bool:
    return normalise(value).startswith("yes")


def split_multi(value: Any) -> List[str]:
    """Forms writes multi-select answers as one semicolon separated string."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    return [part.strip() for part in re.split(r"[;\n]", str(value)) if part.strip()]


def mean(values: Sequence[float], default: float = 0.0) -> float:
    return sum(values) / len(values) if values else default


# ---------------------------------------------------------------------------
# Scoring one department
# ---------------------------------------------------------------------------

@dataclass
class DepartmentEvidence:
    """Everything the drill-down needs that is not a score."""

    sessions_per_week: float = 0.0
    tools: List[List[Any]] = None
    processes: List[str] = None
    ideas: List[str] = None
    gap: str = "Not recorded"
    opportunity: str = "Not recorded"

    def __post_init__(self):
        self.tools = self.tools or []
        self.processes = self.processes or []
        self.ideas = self.ideas or []


def score_department(
    rows: Sequence[Dict[str, Any]], mapping: ColumnMap
) -> Tuple[IndicatorScores, DepartmentEvidence, int]:
    """
    Returns the eight indicator scores, the supporting evidence, and the number
    of people who reported using AI.

    Non-users stay in the denominator throughout. A department where three
    enthusiasts answered and thirty non-users also answered is not a well
    adopted department, and excluding the non-users would say that it is.
    """
    total = len(rows)
    if total == 0:
        return IndicatorScores(), DepartmentEvidence(), 0

    users = [r for r in rows if is_yes(mapping.get("used_30d", r))]
    user_ids = {id(r) for r in users}

    def is_user(row: Dict[str, Any]) -> bool:
        return id(row) in user_ids

    # 1. Active AI users
    active_users = len(users) / total * 100

    # 2. Usage frequency. Days times sessions per day, scored against the target.
    sessions = [
        lookup(mapping.get("days", r), DAYS_PER_WEEK) * lookup(mapping.get("times", r), TIMES_PER_DAY)
        if is_user(r) else 0.0
        for r in rows
    ]
    avg_sessions = mean(sessions)
    frequency = scale_to_target(avg_sessions, SESSIONS_PER_WEEK_TARGET)

    # 3. Training completion. Any "Yes, ..." option counts.
    trained = sum(
        1 for r in rows
        if any(normalise(a).startswith("yes") for a in split_multi(mapping.get("training", r)))
    )
    training = trained / total * 100

    # 4. AI in weekly workflow
    workflow = mean([
        lookup(mapping.get("workflow", r), WORKFLOW_POINTS) if is_user(r) else 0.0
        for r in rows
    ])

    # 5. AI-assisted task volume
    task_counts = [
        lookup(mapping.get("task_count", r), TASKS_PER_MONTH) if is_user(r) else 0.0
        for r in rows
    ]
    task_volume = scale_to_target(mean(task_counts), TASKS_PER_MONTH_TARGET)

    # 6. Eligible workflows covered
    coverage = mean([
        lookup(mapping.get("coverage", r), COVERAGE_POINTS) if is_user(r) else 0.0
        for r in rows
    ])

    # 7. Proficiency. Everyone answers, including non-users, so this measures
    #    whole-department readiness rather than the readiness of the keen few.
    proficiency_scores: List[float] = []
    for r in rows:
        asked = correct = 0
        for label, column in mapping.knowledge.items():
            if column is None:
                continue
            asked += 1
            if KNOWLEDGE_ANSWERS[label] in normalise(r.get(column)):
                correct += 1
        if asked:
            proficiency_scores.append(correct / asked * 100)
    proficiency = mean(proficiency_scores)

    # 8. Safe use. Users only: a non-user cannot paste anything anywhere.
    #    Averaging non-users in at 100 would reward a department for not using AI.
    safe_scores: List[float] = []
    for r in users:
        score = 100.0 - lookup(mapping.get("account", r), ACCOUNT_PENALTY)
        for item in split_multi(mapping.get("pasted", r)):
            answer = normalise(item)
            if answer.startswith("none of the above"):
                continue
            score -= PREFER_NOT_TO_SAY_PENALTY if "prefer not to say" in answer else SENSITIVE_CATEGORY_PENALTY
        safe_scores.append(max(0.0, score))
    safe_use = mean(safe_scores)

    scores = IndicatorScores(
        users=round(active_users, 1),
        freq=round(frequency, 1),
        train=round(training, 1),
        flow=round(workflow, 1),
        tasks=round(task_volume, 1),
        cover=round(coverage, 1),
        prof=round(proficiency, 1),
        comp=round(safe_use, 1),
    )

    return scores, _evidence(rows, users, mapping, avg_sessions), len(users)


def _evidence(
    rows: Sequence[Dict[str, Any]],
    users: Sequence[Dict[str, Any]],
    mapping: ColumnMap,
    avg_sessions: float,
) -> DepartmentEvidence:
    """The narrative half of the drill-down, built from what people selected and wrote."""
    tool_counts: Counter = Counter()
    for r in users:
        for tool in split_multi(mapping.get("tools", r)):
            tool_counts[tool] += 1
    denominator = max(1, len(users))
    tools = [[name, round(count / denominator * 100)] for name, count in tool_counts.most_common(3)]

    process_counts: Counter = Counter()
    for r in users:
        for task in split_multi(mapping.get("regular_tasks", r)):
            if not normalise(task).startswith("none of these"):
                process_counts[task] += 1
    processes = [name for name, _ in process_counts.most_common(4)]

    ideas: List[str] = []
    for r in rows:
        for column in mapping.ideas:
            text = str(r.get(column) or "").strip()
            if text and text.lower() != "nan":
                ideas.append(text)

    blocker_counts: Counter = Counter()
    for r in rows:
        for blocker in split_multi(mapping.get("blockers", r)):
            if not normalise(blocker).startswith("nothing stops me"):
                blocker_counts[blocker] += 1

    # The most common idea, not the first one typed. One person's answer is not
    # a department's opportunity; a repeated answer is.
    idea_counts = Counter(normalise(i) for i in ideas)
    top_idea = ""
    if idea_counts:
        wanted = idea_counts.most_common(1)[0][0]
        top_idea = next(i for i in ideas if normalise(i) == wanted)

    return DepartmentEvidence(
        sessions_per_week=round(avg_sessions, 1),
        tools=tools,
        processes=processes,
        ideas=ideas,
        gap=blocker_counts.most_common(1)[0][0] if blocker_counts else "Not recorded",
        opportunity=top_idea or "Not recorded",
    )


# ---------------------------------------------------------------------------
# Scoring a whole wave
# ---------------------------------------------------------------------------

@dataclass
class IngestReport:
    """What happened during an import, so problems surface instead of hiding."""

    responses: int = 0
    departments: int = 0
    missing_columns: List[str] = None
    knowledge_questions_found: int = 0
    unmatched_departments: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        self.missing_columns = self.missing_columns or []
        self.unmatched_departments = self.unmatched_departments or []
        self.warnings = self.warnings or []


def ingest_wave(
    frame: pd.DataFrame,
    headcounts: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[List[DepartmentResult], IngestReport]:
    """
    Score every department in one survey export.

    `headcounts` is keyed by normalised department name and supplies the true
    staff numbers from HR. Without it the number of respondents is used as the
    headcount, which makes every response rate 100% and is only ever right by
    accident, so a warning is raised.
    """
    headcounts = headcounts or {}
    mapping = map_columns(frame)

    report = IngestReport(
        responses=len(frame),
        missing_columns=mapping.missing,
        knowledge_questions_found=sum(1 for c in mapping.knowledge.values() if c),
    )

    if mapping.columns.get("department") is None:
        raise ValueError(
            "Could not find the department question. "
            "Add a distinctive phrase to COLUMN_HINTS['department']."
        )
    if not headcounts:
        report.warnings.append(
            "No headcount file supplied, so response rates cannot be calculated "
            "and every department will look fully surveyed."
        )

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in frame.to_dict("records"):
        name = str(mapping.get("department", row) or "").strip()
        if not name or name.lower() == "nan":
            continue
        grouped.setdefault(normalise(name), []).append(row)

    results: List[DepartmentResult] = []
    for key, rows in sorted(grouped.items()):
        scores, evidence, user_count = score_department(rows, mapping)

        hr = headcounts.get(key)
        if hr is None:
            report.unmatched_departments.append(str(mapping.get("department", rows[0])).strip())

        display_name = (hr or {}).get("name") or str(mapping.get("department", rows[0])).strip()
        headcount = int((hr or {}).get("staff") or len(rows))

        result = DepartmentResult(
            name=display_name,
            function=(hr or {}).get("function", "Unassigned"),
            headcount=headcount,
            respondents=len(rows),
            active_users=round(scores.users / 100 * headcount),
            scores=scores,
            sessions_per_week=evidence.sessions_per_week,
            use_cases=len(set(normalise(i) for i in evidence.ideas)) + len(evidence.processes),
            tools=evidence.tools,
            processes=evidence.processes,
            gap=evidence.gap,
            opportunity=evidence.opportunity,
        )

        if result.reliability() == "insufficient":
            report.warnings.append(
                f"{display_name}: only {result.response_rate}% responded, "
                "too few to draw conclusions from."
            )
        elif result.reliability() == "provisional":
            report.warnings.append(
                f"{display_name}: {result.response_rate}% responded, treat as provisional."
            )
        if 0 < user_count < 5:
            report.warnings.append(
                f"{display_name}: safe-use score is based on {user_count} AI users, "
                "too few to be a department score."
            )

        results.append(result)

    report.departments = len(results)
    return results, report
