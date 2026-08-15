"""Department administration."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, require_roles, visible_department_ids
from app.models.models import Department, Role
from app.schemas.schemas import DepartmentIn, DepartmentOut

router = APIRouter(prefix="/departments", tags=["departments"])

Manager = Depends(require_roles(Role.ADMIN, Role.LEADERSHIP))


@router.get("", response_model=list[DepartmentOut])
def list_departments(db: DbSession, user: CurrentUser) -> list[Department]:
    rows = db.scalars(select(Department).order_by(Department.name)).all()
    allowed = visible_department_ids(user)
    if allowed is None:
        return list(rows)
    return [d for d in rows if d.id in allowed]


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED, dependencies=[Manager])
def create_department(payload: DepartmentIn, db: DbSession) -> Department:
    if db.scalar(select(Department).where(Department.name == payload.name)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A department with that name already exists",
        )
    department = Department(**payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.patch("/{department_id}", response_model=DepartmentOut, dependencies=[Manager])
def update_department(department_id: int, payload: DepartmentIn, db: DbSession) -> Department:
    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    department.name = payload.name
    department.function = payload.function
    db.commit()
    db.refresh(department)
    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Manager])
def retire_department(department_id: int, db: DbSession) -> None:
    """
    Retired, not deleted.

    Historical waves point at this row. Deleting it would either break those
    records or silently rewrite what a past report said.
    """
    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    department.is_active = False
    db.commit()
