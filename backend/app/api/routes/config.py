"""Weights and targets: the parts leadership is meant to change."""

from datetime import date

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models.models import Department, Role, Target, WeightSet
from app.schemas.schemas import TargetsIn, WeightsIn
from app.services.dashboard import active_weights, targets_payload
from fastapi import Depends

router = APIRouter(prefix="/config", tags=["configuration"])

Editor = Depends(require_roles(Role.ADMIN, Role.LEADERSHIP))


@router.get("/weights")
def get_weights(db: DbSession, _: CurrentUser) -> dict:
    return active_weights(db)


@router.put("/weights", dependencies=[Editor])
def set_weights(payload: WeightsIn, db: DbSession) -> dict:
    """
    Saved as a new active set rather than an edit in place.

    Versioning matters: a report produced last quarter must still be
    reproducible after somebody changes what adoption means.
    """
    for existing in db.scalars(select(WeightSet).where(WeightSet.is_active.is_(True))).all():
        existing.is_active = False

    weight_set = WeightSet(
        name=payload.name, weights=payload.weights, note=payload.note, is_active=True
    )
    db.add(weight_set)
    db.commit()
    return active_weights(db)


@router.get("/targets")
def get_targets(db: DbSession, _: CurrentUser) -> dict:
    return targets_payload(db)


@router.put("/targets", dependencies=[Editor])
def set_targets(payload: TargetsIn, db: DbSession) -> dict:
    today = date.today()

    org = db.scalar(select(Target).where(Target.department_id.is_(None)))
    if org is None:
        org = Target(department_id=None, value=payload.org, effective_from=today)
        db.add(org)
    org.value = payload.org
    org.minimum = payload.minimum

    departments = {d.name.lower(): d for d in db.scalars(select(Department)).all()}
    slugs = {
        "".join(ch if ch.isalnum() else "-" for ch in name).strip("-"): dept
        for name, dept in departments.items()
    }

    for slug, value in payload.by_department.items():
        department = slugs.get(slug)
        if department is None:
            continue
        row = db.scalar(select(Target).where(Target.department_id == department.id))
        if row is None:
            row = Target(department_id=department.id, value=value, effective_from=today)
            db.add(row)
        else:
            row.value = value

    db.commit()
    return targets_payload(db)
