

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

# JSONB in Postgres, plain JSON everywhere else. Production runs on Postgres and
# gets the indexable type; the test suite runs on in-memory SQLite and stays fast
# without needing a database server.
JSONType = JSON().with_variant(JSONB(), "postgresql")


class Role(str, enum.Enum):
    """
    Who can see what.

    LEADERSHIP sees every department. HOD sees only their own. VIEWER sees the
    organisation totals but no department breakdown. This matters: publishing a
    league table of departments to everyone changes how people answer the next
    survey, and the survey promised department-level reporting only.
    """

    ADMIN = "admin"
    LEADERSHIP = "leadership"
    HOD = "hod"
    VIEWER = "viewer"


class WaveStatus(str, enum.Enum):
    DRAFT = "draft"           # created, no responses loaded
    COLLECTING = "collecting"  # survey open
    SCORED = "scored"          # responses loaded and scored
    PUBLISHED = "published"    # visible on the dashboard


# ---------------------------------------------------------------------------
# Organisation
# ---------------------------------------------------------------------------

class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    function: Mapped[str] = mapped_column(String(80), default="Unassigned", nullable=False)

    # Departments are retired rather than deleted, so historical waves keep
    # pointing at something real.
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    headcounts: Mapped[List["Headcount"]] = relationship(back_populates="department")
    scores: Mapped[List["DepartmentScore"]] = relationship(back_populates="department")
    users: Mapped[List["User"]] = relationship(back_populates="department")

    def __repr__(self) -> str:
        return f"<Department {self.name}>"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.VIEWER, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Only set for heads of department, and only they are scoped by it.
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    department: Mapped[Optional[Department]] = relationship(back_populates="users")


# ---------------------------------------------------------------------------
# Waves
# ---------------------------------------------------------------------------

class Wave(Base, TimestampMixin):
    __tablename__ = "waves"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    opened_on: Mapped[Optional[date]] = mapped_column(Date)
    closed_on: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[WaveStatus] = mapped_column(Enum(WaveStatus), default=WaveStatus.DRAFT)

    # Ordering for the trend chart. Explicit rather than inferred from dates,
    # because a wave can be re-run and the labels are what leadership reads.
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    headcounts: Mapped[List["Headcount"]] = relationship(back_populates="wave")
    responses: Mapped[List["SurveyResponse"]] = relationship(back_populates="wave")
    scores: Mapped[List["DepartmentScore"]] = relationship(back_populates="wave")

    __table_args__ = (UniqueConstraint("sequence", name="uq_wave_sequence"),)


class Headcount(Base, TimestampMixin):
    """Staff numbers for one department at one wave, from the HR file."""

    __tablename__ = "headcounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    wave_id: Mapped[int] = mapped_column(ForeignKey("waves.id", ondelete="CASCADE"))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))

    total: Mapped[int] = mapped_column(Integer, nullable=False)
    leadership: Mapped[int] = mapped_column(Integer, default=0)
    managers: Mapped[int] = mapped_column(Integer, default=0)
    specialists: Mapped[int] = mapped_column(Integer, default=0)
    support: Mapped[int] = mapped_column(Integer, default=0)

    wave: Mapped[Wave] = relationship(back_populates="headcounts")
    department: Mapped[Department] = relationship(back_populates="headcounts")

    __table_args__ = (
        UniqueConstraint("wave_id", "department_id", name="uq_headcount_wave_dept"),
    )


# ---------------------------------------------------------------------------
# Survey data
# ---------------------------------------------------------------------------

class SurveyResponse(Base, TimestampMixin):
    """
    One person's answers, stored as submitted.

    The answers live in a JSONB column rather than 40 typed columns. Survey
    wording changes between waves, and a rigid schema would need a migration
    every time a question is added. JSONB keeps the raw record intact and the
    scoring service is the only thing that needs to understand its shape.

    No name or email is stored. The survey promised anonymity, and a
    self-generated linking code is enough to match a person across waves.
    """

    __tablename__ = "survey_responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    wave_id: Mapped[int] = mapped_column(ForeignKey("waves.id", ondelete="CASCADE"))
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))

    linking_code: Mapped[Optional[str]] = mapped_column(String(8), index=True)
    employee_level: Mapped[Optional[str]] = mapped_column(String(40))
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    answers: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    wave: Mapped[Wave] = relationship(back_populates="responses")

    __table_args__ = (
        Index("ix_response_wave_dept", "wave_id", "department_id"),
    )


class DepartmentScore(Base, TimestampMixin):
    """
    Calculated indicator scores for one department in one wave.

    The eight indicator values are stored, but the adoption rate is not. That
    number depends on the weights, and the weights are adjustable in the
    dashboard, so storing it would mean a saved figure that silently disagrees
    with what the screen shows.
    """

    __tablename__ = "department_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    wave_id: Mapped[int] = mapped_column(ForeignKey("waves.id", ondelete="CASCADE"))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))

    users: Mapped[float] = mapped_column(Float, default=0)
    freq: Mapped[float] = mapped_column(Float, default=0)
    train: Mapped[float] = mapped_column(Float, default=0)
    flow: Mapped[float] = mapped_column(Float, default=0)
    tasks: Mapped[float] = mapped_column(Float, default=0)
    cover: Mapped[float] = mapped_column(Float, default=0)
    prof: Mapped[float] = mapped_column(Float, default=0)
    comp: Mapped[float] = mapped_column(Float, default=0)
    agent: Mapped[float] = mapped_column(Float, default=0)
    automate: Mapped[float] = mapped_column(Float, default=0)

    ai_solutions: Mapped[int] = mapped_column(Integer, default=0)
    ai_solutions_personal: Mapped[int] = mapped_column(Integer, default=0)

    respondents: Mapped[int] = mapped_column(Integer, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    sessions_per_week: Mapped[float] = mapped_column(Float, default=0)
    use_cases: Mapped[int] = mapped_column(Integer, default=0)

    # Narrative for the drill-down, derived from the free-text answers.
    top_tools: Mapped[list] = mapped_column(JSONType, default=list)
    processes: Mapped[list] = mapped_column(JSONType, default=list)
    gap: Mapped[Optional[str]] = mapped_column(Text)
    opportunity: Mapped[Optional[str]] = mapped_column(Text)

    wave: Mapped[Wave] = relationship(back_populates="scores")
    department: Mapped[Department] = relationship(back_populates="scores")

    __table_args__ = (
        UniqueConstraint("wave_id", "department_id", name="uq_score_wave_dept"),
    )


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class WeightSet(Base, TimestampMixin):
    """
    A named set of indicator weights.

    Versioned rather than overwritten. When leadership changes what matters,
    the old set stays so a past report can be reproduced exactly.
    """

    __tablename__ = "weight_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)
    weights: Mapped[dict] = mapped_column(JSONType, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text)


class Target(Base, TimestampMixin):
    """
    An adoption target. A row with no department is the organisation-wide one.
    """

    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    value: Mapped[float] = mapped_column(Float, nullable=False)
    minimum: Mapped[Optional[float]] = mapped_column(Float)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        Index("ix_target_dept_from", "department_id", "effective_from"),
    )
