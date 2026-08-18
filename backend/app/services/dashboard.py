"""
Assembling the dashboard payload.

Kept out of the route handlers because it is the one piece of read logic with
real decisions in it: which waves to include, which departments the caller may
see, and how a department that appears in one wave but not another is handled.
Routes stay thin and this stays testable.
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence, Set

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import (
    Department,
    DepartmentScore,
    Headcount,
    Target,
    WeightSet,
    Wave,
    WaveStatus,
)
from app.services.scoring import DEFAULT_WEIGHTS, Indicator

INDICATOR_KEYS = [i.value for i in Indicator]


def active_weights(db: Session) -> Dict[str, float]:
    weight_set = db.scalar(select(WeightSet).where(WeightSet.is_active.is_(True)))
    if weight_set is None:
        return dict(DEFAULT_WEIGHTS)
    # Fill any gaps from the defaults, so adding a ninth indicator later does not
    # break every saved weight set.
    return {**DEFAULT_WEIGHTS, **(weight_set.weights or {})}


def targets_payload(db: Session) -> Dict[str, object]:
    rows = db.scalars(select(Target)).all()
    org = next((t for t in rows if t.department_id is None), None)
    by_department: Dict[str, float] = {}
    for target in rows:
        if target.department_id is None:
            continue
        department = db.get(Department, target.department_id)
        if department:
            by_department[_slug(department.name)] = target.value
    return {
        "org": org.value if org else 70.0,
        "quarter": org.value if org else 65.0,
        "min": (org.minimum if org and org.minimum is not None else 40.0),
        "byDept": by_department,
    }


def _slug(value: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "dept"


def build_dashboard(
    db: Session,
    visible_ids: Optional[Set[int]] = None,
    include_unpublished: bool = False,
) -> Dict[str, object]:
    """
    The full payload the front end expects.

    Only published waves are returned by default. A wave that has been scored but
    not published is still being checked, and half-checked figures reaching
    leadership is exactly the failure this status field exists to prevent.
    """
    statuses = (
        [WaveStatus.SCORED, WaveStatus.PUBLISHED] if include_unpublished else [WaveStatus.PUBLISHED]
    )
    waves: Sequence[Wave] = db.scalars(
        select(Wave).where(Wave.status.in_(statuses)).order_by(Wave.sequence)
    ).all()

    payload_waves = []
    for wave in waves:
        scores = db.scalars(
            select(DepartmentScore).where(DepartmentScore.wave_id == wave.id)
        ).all()
        headcounts = {
            h.department_id: h
            for h in db.scalars(select(Headcount).where(Headcount.wave_id == wave.id)).all()
        }

        departments = []
        for score in scores:
            if visible_ids is not None and score.department_id not in visible_ids:
                continue
            department = db.get(Department, score.department_id)
            if department is None:
                continue
            headcount = headcounts.get(score.department_id)
            departments.append(
                {
                    "name": department.name,
                    "function": department.function,
                    "staff": headcount.total if headcount else 0,
                    "mix": {
                        "leadership": headcount.leadership if headcount else 0,
                        "manager": headcount.managers if headcount else 0,
                        "specialist": headcount.specialists if headcount else 0,
                        "support": headcount.support if headcount else 0,
                    },
                    "metrics": {key: getattr(score, key) for key in INDICATOR_KEYS},
                    "sessions": score.sessions_per_week,
                    "cases": score.use_cases,
                    "aiSolutions": score.ai_solutions,
                    "aiSolutionsPersonal": score.ai_solutions_personal,
                    "tools": score.top_tools or [],
                    "processes": score.processes or [],
                    "gap": score.gap or "Not recorded",
                    "opportunity": score.opportunity or "Not recorded",
                    "respondents": score.respondents,
                    "reliability": _reliability(score.respondents, headcount.total if headcount else 0),
                }
            )

        payload_waves.append({"label": wave.label, "departments": departments})

    return {
        "waves": payload_waves,
        "weights": active_weights(db),
        "targets": targets_payload(db),
    }


def _reliability(respondents: int, headcount: int) -> str:
    """
    With no telemetry behind the numbers, a score is only as good as who
    answered. The thresholds come from the survey design and are applied here so
    the API can never hand a thin sample to the UI without a label on it.
    """
    if headcount <= 0:
        return "insufficient"
    rate = respondents / headcount * 100
    if rate >= 60:
        return "reliable"
    if rate >= 40:
        return "provisional"
    return "insufficient"
