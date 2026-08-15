"""
Waves and survey uploads.

This is where a spreadsheet becomes numbers on a dashboard. The upload endpoint
does four things in one transaction: store the raw responses, score them, write
the department scores, and record the headcounts. Doing it atomically matters,
because a half-imported wave would show some departments at their new figures
and others at their old ones, with nothing on screen to say so.
"""

from __future__ import annotations

import io
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import delete, select

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.models import (
    Department,
    DepartmentScore,
    Headcount,
    Role,
    SurveyResponse,
    Wave,
    WaveStatus,
)
from app.schemas.schemas import IngestSummary, WaveIn, WaveOut
from app.services.ingest import ingest_wave, map_columns, normalise
from app.services.scoring import Indicator

router = APIRouter(prefix="/waves", tags=["waves"])

Manager = Depends(require_roles(Role.ADMIN, Role.LEADERSHIP))
INDICATOR_KEYS = [i.value for i in Indicator]

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.get("", response_model=list[WaveOut])
def list_waves(db: DbSession, _: CurrentUser) -> list[Wave]:
    return list(db.scalars(select(Wave).order_by(Wave.sequence)).all())


@router.post("", response_model=WaveOut, status_code=status.HTTP_201_CREATED, dependencies=[Manager])
def create_wave(payload: WaveIn, db: DbSession) -> Wave:
    if db.scalar(select(Wave).where(Wave.sequence == payload.sequence)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A wave with sequence {payload.sequence} already exists",
        )
    wave = Wave(**payload.model_dump())
    db.add(wave)
    db.commit()
    db.refresh(wave)
    return wave


@router.post("/{wave_id}/publish", response_model=WaveOut, dependencies=[Manager])
def publish_wave(wave_id: int, db: DbSession) -> Wave:
    wave = _get_wave(db, wave_id)
    if wave.status == WaveStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Load and score the responses before publishing this wave",
        )
    wave.status = WaveStatus.PUBLISHED
    db.commit()
    db.refresh(wave)
    return wave


def _read_upload(file: UploadFile) -> pd.DataFrame:
    raw = file.file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="That file is larger than 10 MB",
        )
    name = (file.filename or "").lower()
    try:
        frame = pd.read_csv(io.BytesIO(raw)) if name.endswith(".csv") else pd.read_excel(io.BytesIO(raw))
    except Exception as exc:  # noqa: BLE001 - anything pandas raises becomes a 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read that file: {exc}",
        ) from exc

    # A file can parse and still be useless. An empty frame or one with no
    # headings is a user error, not a server error, so say so plainly.
    if frame.empty or frame.columns.empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That file has no rows the importer could read",
        )
    return frame


def _headcount_lookup(db: DbSession) -> dict[str, dict]:
    return {
        normalise(d.name): {"name": d.name, "function": d.function, "staff": 0}
        for d in db.scalars(select(Department)).all()
    }


@router.post("/{wave_id}/responses", response_model=IngestSummary, dependencies=[Manager])
def upload_responses(
    wave_id: int,
    db: DbSession,
    file: UploadFile = File(..., description="Survey export, xlsx or csv"),
    headcount_file: Optional[UploadFile] = File(None, description="HR headcount, xlsx or csv"),
) -> IngestSummary:
    """
    Load one wave of survey responses.

    Re-uploading replaces everything for that wave. Merging would silently
    double-count anyone who appeared in both files, and the resulting numbers
    would be wrong in a way nobody could see.
    """
    wave = _get_wave(db, wave_id)
    frame = _read_upload(file)

    headcounts = _headcount_lookup(db)
    if headcount_file is not None:
        headcounts = _parse_headcounts(_read_upload(headcount_file), headcounts)

    results, report = ingest_wave(frame, headcounts)
    mapping = map_columns(frame)

    # Replace rather than append, in one transaction.
    db.execute(delete(SurveyResponse).where(SurveyResponse.wave_id == wave.id))
    db.execute(delete(DepartmentScore).where(DepartmentScore.wave_id == wave.id))
    db.execute(delete(Headcount).where(Headcount.wave_id == wave.id))

    departments = {normalise(d.name): d for d in db.scalars(select(Department)).all()}

    # Keep the raw answers. Scores are derived data; if a rule is ever corrected
    # the wave can be re-scored, which is impossible once the source is gone.
    for row in frame.to_dict("records"):
        name = str(mapping.get("department", row) or "").strip()
        department = departments.get(normalise(name))
        db.add(
            SurveyResponse(
                wave_id=wave.id,
                department_id=department.id if department else None,
                linking_code=str(mapping.get("linking_code", row) or "")[:8] or None,
                employee_level=str(mapping.get("level", row) or "")[:40] or None,
                answers={str(k): _clean(v) for k, v in row.items()},
            )
        )

    for result in results:
        department = departments.get(normalise(result.name))
        if department is None:
            department = Department(name=result.name, function=result.function)
            db.add(department)
            db.flush()
            departments[normalise(result.name)] = department

        db.add(
            DepartmentScore(
                wave_id=wave.id,
                department_id=department.id,
                **{key: getattr(result.scores, key) for key in INDICATOR_KEYS},
                respondents=result.respondents,
                active_users=result.active_users,
                sessions_per_week=result.sessions_per_week,
                use_cases=result.use_cases,
                top_tools=result.tools,
                processes=result.processes,
                gap=result.gap,
                opportunity=result.opportunity,
            )
        )

        hr = headcounts.get(normalise(result.name), {})
        mix = hr.get("mix", {})
        db.add(
            Headcount(
                wave_id=wave.id,
                department_id=department.id,
                total=result.headcount,
                leadership=mix.get("leadership", 0),
                managers=mix.get("manager", 0),
                specialists=mix.get("specialist", 0),
                support=mix.get("support", 0),
            )
        )

    wave.status = WaveStatus.SCORED
    db.commit()

    return IngestSummary(
        wave_id=wave.id,
        wave_label=wave.label,
        responses=report.responses,
        departments=report.departments,
        missing_columns=report.missing_columns,
        knowledge_questions_found=report.knowledge_questions_found,
        unmatched_departments=report.unmatched_departments,
        warnings=report.warnings,
    )


def _get_wave(db: DbSession, wave_id: int) -> Wave:
    wave = db.get(Wave, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    return wave


def _clean(value: object) -> object:
    """NaN is not valid JSON, and pandas produces it for every blank cell."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _parse_headcounts(frame: pd.DataFrame, fallback: dict[str, dict]) -> dict[str, dict]:
    lookup = {normalise(c): c for c in frame.columns}

    def column(*names: str) -> Optional[str]:
        for wanted in names:
            for heading, original in lookup.items():
                if wanted in heading:
                    return original
        return None

    name_col = column("department")
    total_col = column("total", "headcount", "staff")
    if not name_col or not total_col:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The headcount file needs a department column and a total headcount column",
        )

    out = dict(fallback)
    for _, row in frame.iterrows():
        name = str(row[name_col]).strip()
        if not name or name.lower() == "nan":
            continue
        key = normalise(name)
        out[key] = {
            "name": name,
            "function": out.get(key, {}).get("function", "Unassigned"),
            "staff": int(row[total_col]),
            "mix": {
                "leadership": _int(row, column("leadership")),
                "manager": _int(row, column("manager")),
                "specialist": _int(row, column("specialist")),
                "support": _int(row, column("support")),
            },
        }
    return out


def _int(row: pd.Series, column: Optional[str]) -> int:
    if not column or column not in row or pd.isna(row[column]):
        return 0
    return int(row[column])
