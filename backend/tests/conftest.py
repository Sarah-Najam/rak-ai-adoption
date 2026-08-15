"""
Shared test fixtures.

The suite runs against in-memory SQLite rather than a real Postgres. Tests that
need a database server are tests people stop running, and the JSON columns are
declared with a dialect variant so both behave the same. Anything genuinely
Postgres-specific belongs in a migration test, not here.
"""

from __future__ import annotations

from datetime import date
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.models import (
    Department,
    DepartmentScore,
    Headcount,
    Role,
    Target,
    User,
    Wave,
    WaveStatus,
    WeightSet,
)
from app.services.scoring import DEFAULT_WEIGHTS


@pytest.fixture
def engine():
    # StaticPool keeps one connection alive, so an in-memory database survives
    # between the test and the request handler.
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db(engine) -> Generator[Session, None, None]:
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine, db) -> Generator[TestClient, None, None]:
    def override() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

PASSWORD = "correct-horse-battery"


@pytest.fixture
def departments(db: Session) -> dict[str, Department]:
    rows = {
        "it": Department(name="Information Technology", function="Technology"),
        "ops": Department(name="Operations", function="Technical"),
    }
    db.add_all(rows.values())
    db.commit()
    for d in rows.values():
        db.refresh(d)
    return rows


@pytest.fixture
def users(db: Session, departments) -> dict[str, User]:
    rows = {
        "admin": User(
            email="admin@rakproperties.ae", full_name="Admin",
            hashed_password=hash_password(PASSWORD), role=Role.ADMIN,
        ),
        "leadership": User(
            email="ceo@rakproperties.ae", full_name="Leadership",
            hashed_password=hash_password(PASSWORD), role=Role.LEADERSHIP,
        ),
        "hod": User(
            email="hod.it@rakproperties.ae", full_name="Head of IT",
            hashed_password=hash_password(PASSWORD), role=Role.HOD,
            department_id=departments["it"].id,
        ),
        "viewer": User(
            email="viewer@rakproperties.ae", full_name="Viewer",
            hashed_password=hash_password(PASSWORD), role=Role.VIEWER,
        ),
        "disabled": User(
            email="left@rakproperties.ae", full_name="Former Colleague",
            hashed_password=hash_password(PASSWORD), role=Role.LEADERSHIP, is_active=False,
        ),
    }
    db.add_all(rows.values())
    db.commit()
    for u in rows.values():
        db.refresh(u)
    return rows


@pytest.fixture
def published_wave(db: Session, departments) -> Wave:
    wave = Wave(label="Wave 1 (before training)", sequence=1, status=WaveStatus.PUBLISHED)
    db.add(wave)
    db.flush()

    scores = {
        "it": dict(users=92, freq=95, train=98, flow=90, tasks=88, cover=86, prof=94, comp=98),
        "ops": dict(users=34, freq=36, train=44, flow=32, tasks=38, cover=30, prof=34, comp=54),
    }
    staff = {"it": 24, "ops": 41}
    for key, department in departments.items():
        db.add(DepartmentScore(
            wave_id=wave.id, department_id=department.id,
            respondents=staff[key], active_users=int(staff[key] * scores[key]["users"] / 100),
            sessions_per_week=4.0, use_cases=5,
            top_tools=[["Claude", 80]], processes=["Drafting"],
            gap="Not recorded", opportunity="Not recorded",
            **scores[key],
        ))
        db.add(Headcount(
            wave_id=wave.id, department_id=department.id, total=staff[key],
            leadership=1, managers=4, specialists=staff[key] - 9, support=4,
        ))

    db.add(WeightSet(name="Default", weights=dict(DEFAULT_WEIGHTS), is_active=True))
    db.add(Target(department_id=None, value=70, minimum=40, effective_from=date(2026, 8, 1)))
    db.commit()
    db.refresh(wave)
    return wave


@pytest.fixture
def token(client: TestClient, users):
    def _token(key: str = "leadership") -> str:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": users[key].email, "password": PASSWORD},
        )
        assert response.status_code == 200, response.text
        return response.json()["access_token"]

    return _token


@pytest.fixture
def auth(token):
    def _auth(key: str = "leadership") -> dict[str, str]:
        return {"Authorization": f"Bearer {token(key)}"}

    return _auth
