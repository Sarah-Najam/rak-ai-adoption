"""The main read endpoint the front end calls."""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession, visible_department_ids
from app.models.models import Role
from app.services.dashboard import build_dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard(db: DbSession, user: CurrentUser) -> dict:
    """
    Everything the dashboard needs, scoped to what this user may see.

    Admins can also see waves that are scored but not yet published, so results
    can be checked before leadership sees them.
    """
    return build_dashboard(
        db,
        visible_ids=visible_department_ids(user),
        include_unpublished=user.role == Role.ADMIN,
    )
