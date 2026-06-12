from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models.maintenance_job import MaintenanceJob
from app.models.user import User
from app.schemas.maintenance import MaintenanceJobCreate, MaintenanceJobUpdate
from app.utils.search import search_patterns


def _latest_ordering():
    return MaintenanceJob.updated_at.desc(), MaintenanceJob.id.desc()


def _query_jobs(search: Optional[str] = None):
    statement = select(MaintenanceJob)
    if search:
        patterns = search_patterns(search)
        if patterns:
            statement = statement.where(
                or_(
                    *[
                        column.ilike(pattern)
                        for pattern in patterns
                        for column in (
                            MaintenanceJob.job_code,
                            MaintenanceJob.machine,
                            MaintenanceJob.team,
                            MaintenanceJob.priority,
                            MaintenanceJob.status,
                            cast(MaintenanceJob.breakdown_from, String),
                            cast(MaintenanceJob.breakdown_to, String),
                            MaintenanceJob.reason,
                            cast(MaintenanceJob.due_by, String),
                        )
                    ]
                )
            )
    return statement


def _job_code(entry_id: int) -> str:
    return f"MT-{entry_id:05d}"


def list_maintenance_jobs(db: Session, search: Optional[str] = None) -> tuple[list[MaintenanceJob], int]:
    base_statement = _query_jobs(search)
    total = db.scalar(select(func.count()).select_from(base_statement.subquery())) or 0
    items = list(db.scalars(base_statement.order_by(*_latest_ordering()).limit(500)).all())
    return items, int(total)


def create_maintenance_job(db: Session, payload: MaintenanceJobCreate, user: User) -> MaintenanceJob:
    entry = MaintenanceJob(
        **payload.model_dump(),
        job_code=f"MT-PENDING-{uuid4().hex[:12]}",
        created_by=user.name,
        updated_at=datetime.utcnow(),
    )
    db.add(entry)
    db.flush()
    entry.job_code = _job_code(entry.id)
    db.commit()
    db.refresh(entry)
    return entry


def update_maintenance_job(db: Session, job_id: int, payload: MaintenanceJobUpdate) -> MaintenanceJob:
    entry = db.get(MaintenanceJob, job_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance job not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    entry.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(entry)
    return entry


def delete_maintenance_job(db: Session, job_id: int) -> None:
    entry = db.get(MaintenanceJob, job_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance job not found")

    db.delete(entry)
    db.commit()
