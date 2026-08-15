"""
Request and response models.

These are the API's contract. They are kept separate from the SQLAlchemy models
on purpose: the database has columns the outside world should never see, such as
hashed passwords, and the dashboard needs shapes that no single table produces.
Letting ORM models leak into responses is how private fields end up in JSON.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.models import Role, WaveStatus
from app.services.scoring import Indicator

INDICATOR_KEYS = [i.value for i in Indicator]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: Role
    department_id: Optional[int] = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8, max_length=72)
    role: Role = Role.VIEWER
    department_id: Optional[int] = None


# ---------------------------------------------------------------------------
# Organisation
# ---------------------------------------------------------------------------

class DepartmentIn(BaseModel):
    name: str
    function: str = "Unassigned"


class DepartmentOut(DepartmentIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool = True


class WaveIn(BaseModel):
    label: str
    sequence: int = 1
    opened_on: Optional[date] = None
    closed_on: Optional[date] = None
    notes: Optional[str] = None


class WaveOut(WaveIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: WaveStatus


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class WeightsIn(BaseModel):
    """
    Weights need not sum to 100. They are normalised before use, so a set
    summing to 87 still produces a valid score rather than an error the user
    cannot act on.
    """

    weights: Dict[str, float]
    name: str = "Custom"
    note: Optional[str] = None


class WeightsOut(BaseModel):
    name: str
    weights: Dict[str, float]
    is_active: bool = True


class TargetsIn(BaseModel):
    org: float = Field(ge=0, le=100)
    quarter: float = Field(ge=0, le=100)
    minimum: float = Field(ge=0, le=100)
    by_department: Dict[str, float] = Field(default_factory=dict)


class TargetsOut(TargetsIn):
    pass


# ---------------------------------------------------------------------------
# Dashboard payload
# ---------------------------------------------------------------------------

class LevelMix(BaseModel):
    leadership: int = 0
    manager: int = 0
    specialist: int = 0
    support: int = 0


class DepartmentSnapshot(BaseModel):
    """One department as measured in one wave."""

    name: str
    function: str = "Unassigned"
    staff: int = 0
    mix: LevelMix = Field(default_factory=LevelMix)
    metrics: Dict[str, float] = Field(default_factory=dict)
    sessions: float = 0
    cases: int = 0
    tools: List[List] = Field(default_factory=list)
    processes: List[str] = Field(default_factory=list)
    gap: str = "Not recorded"
    opportunity: str = "Not recorded"
    respondents: Optional[int] = None
    reliability: Optional[str] = None


class WavePayload(BaseModel):
    label: str
    departments: List[DepartmentSnapshot] = Field(default_factory=list)


class DashboardPayload(BaseModel):
    """
    The whole dashboard in one response.

    One request rather than several, because every panel on the page is derived
    from the same set of numbers. Splitting it would mean the treemap and the
    summary could briefly disagree while the second request was in flight.
    """

    waves: List[WavePayload]
    weights: Dict[str, float]
    targets: Dict[str, object]


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

class IngestSummary(BaseModel):
    """What the importer found, so problems surface immediately."""

    wave_id: int
    wave_label: str
    responses: int
    departments: int
    missing_columns: List[str] = Field(default_factory=list)
    knowledge_questions_found: int = 0
    unmatched_departments: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
