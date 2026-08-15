"""
Create the starting rows a fresh database needs.

Safe to run more than once: every insert checks first. A seed script that
explodes on second run is a seed script people stop trusting.

    python -m scripts.seed
"""

from __future__ import annotations

import os
from datetime import date

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.models import Department, Role, Target, User, WeightSet
from app.services.scoring import DEFAULT_WEIGHTS

DEPARTMENTS = [
    ("Human Resources", "Corporate Services"),
    ("Finance", "Corporate Services"),
    ("Information Technology", "Technology"),
    ("Marketing & Communications", "Commercial"),
    ("Sales", "Commercial"),
    ("Legal", "Corporate Services"),
    ("Procurement", "Corporate Services"),
    ("Operations", "Technical"),
    ("Learning & Development", "Corporate Services"),
    ("Property Management", "Technical"),
    ("Customer Service", "Commercial"),
    ("Project Development", "Technical"),
    ("Administration", "Corporate Services"),
]


def main() -> None:
    db = SessionLocal()
    created = {"departments": 0, "users": 0, "config": 0}
    try:
        for name, function in DEPARTMENTS:
            if db.scalar(select(Department).where(Department.name == name)):
                continue
            db.add(Department(name=name, function=function))
            created["departments"] += 1
        db.commit()

        # Never a default password. An unset variable stops the script rather
        # than leaving an account anyone who has read the repository can use.
        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")
        if not email or not password:
            raise SystemExit(
                "Set ADMIN_EMAIL and ADMIN_PASSWORD before seeding, for example:\n"
                "  ADMIN_EMAIL=you@rakproperties.ae ADMIN_PASSWORD='...' python -m scripts.seed"
            )

        if not db.scalar(select(User).where(User.email == email)):
            db.add(User(
                email=email,
                full_name=os.environ.get("ADMIN_NAME", "Administrator"),
                hashed_password=hash_password(password),
                role=Role.ADMIN,
            ))
            created["users"] += 1

        if not db.scalar(select(WeightSet).where(WeightSet.is_active.is_(True))):
            db.add(WeightSet(name="Default model", weights=dict(DEFAULT_WEIGHTS), is_active=True))
            created["config"] += 1

        if not db.scalar(select(Target).where(Target.department_id.is_(None))):
            db.add(Target(department_id=None, value=70, minimum=40, effective_from=date.today()))
            created["config"] += 1

        db.commit()
        print(
            f"Seeded {created['departments']} departments, "
            f"{created['users']} user(s), {created['config']} config row(s)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
