from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.inventory_entry import InventoryEntry
from app.models.user import User
from app.schemas.inventory import (
    InventoryBalancePreview,
    InventoryEntryCreate,
    InventoryEntryUpdate,
    InventoryMovementPoint,
    InventoryPartBalance,
    InventorySummaryResponse,
)
from app.utils.config import settings


def _entry_ordering():
    return InventoryEntry.date.asc(), InventoryEntry.created_at.asc(), InventoryEntry.id.asc()


def _latest_ordering():
    return InventoryEntry.date.desc(), InventoryEntry.created_at.desc(), InventoryEntry.id.desc()


def _query_entries(
    search: Optional[str] = None,
    part_name: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    statement = select(InventoryEntry)

    if search:
        search_pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                InventoryEntry.part_name.ilike(search_pattern),
                InventoryEntry.remarks.ilike(search_pattern),
                InventoryEntry.created_by.ilike(search_pattern),
            )
        )

    if part_name:
        statement = statement.where(InventoryEntry.part_name == part_name)

    if date_from:
        statement = statement.where(InventoryEntry.date >= date_from)

    if date_to:
        statement = statement.where(InventoryEntry.date <= date_to)

    return statement


def _get_entry(db: Session, entry_id: int) -> InventoryEntry:
    entry = db.get(InventoryEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory entry not found")
    return entry


def _recalculate_part_balances(db: Session, part_name: str) -> None:
    entries = list(
        db.scalars(
            select(InventoryEntry).where(InventoryEntry.part_name == part_name).order_by(*_entry_ordering())
        ).all()
    )

    running_balance = 0
    for entry in entries:
        running_balance += entry.in_quantity
        running_balance -= entry.out_quantity
        running_balance -= entry.rejection_quantity
        entry.balance_quantity = running_balance


def _latest_entries_by_part(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list[InventoryEntry]:
    part_statement = select(InventoryEntry.part_name).distinct().order_by(InventoryEntry.part_name.asc())
    if date_from:
        part_statement = part_statement.where(InventoryEntry.date >= date_from)
    if date_to:
        part_statement = part_statement.where(InventoryEntry.date <= date_to)

    part_names = list(db.scalars(part_statement).all())

    latest_entries: list[InventoryEntry] = []
    for part_name in part_names:
        latest_statement = select(InventoryEntry).where(InventoryEntry.part_name == part_name)
        if date_from:
            latest_statement = latest_statement.where(InventoryEntry.date >= date_from)
        if date_to:
            latest_statement = latest_statement.where(InventoryEntry.date <= date_to)

        latest = db.scalar(latest_statement.order_by(*_latest_ordering()).limit(1))
        if latest:
            latest_entries.append(latest)

    return latest_entries


def _build_part_balance_rows(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list[InventoryPartBalance]:
    latest_entries = _latest_entries_by_part(db, date_from, date_to)
    rows: list[InventoryPartBalance] = []

    for entry in latest_entries:
        totals_statement = select(
            func.coalesce(func.sum(InventoryEntry.in_quantity), 0),
            func.coalesce(func.sum(InventoryEntry.out_quantity), 0),
            func.coalesce(func.sum(InventoryEntry.rejection_quantity), 0),
        ).where(InventoryEntry.part_name == entry.part_name)
        if date_from:
            totals_statement = totals_statement.where(InventoryEntry.date >= date_from)
        if date_to:
            totals_statement = totals_statement.where(InventoryEntry.date <= date_to)

        totals = db.execute(totals_statement).one()
        total_in_quantity, total_out_quantity, total_rejection_quantity = (int(totals[0]), int(totals[1]), int(totals[2]))
        rows.append(
            InventoryPartBalance(
                part_name=entry.part_name,
                balance_quantity=entry.balance_quantity,
                total_in_quantity=total_in_quantity,
                total_out_quantity=total_out_quantity,
                total_rejection_quantity=total_rejection_quantity,
                latest_entry_date=entry.date,
                is_low_inventory=entry.balance_quantity < settings.inventory_low_threshold,
            )
        )

    return sorted(rows, key=lambda row: (row.balance_quantity, row.part_name.lower()))


def list_inventory_entries(
    db: Session,
    search: Optional[str] = None,
    part_name: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> tuple[list[InventoryEntry], int]:
    base_statement = _query_entries(search, part_name, date_from, date_to)
    total = db.scalar(select(func.count()).select_from(base_statement.subquery())) or 0
    items = list(db.scalars(base_statement.order_by(*_latest_ordering()).limit(50)).all())
    return items, int(total)


def list_inventory_logs(
    db: Session,
    page: int,
    page_size: int,
    search: Optional[str] = None,
    part_name: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> tuple[list[InventoryEntry], int]:
    base_statement = _query_entries(search, part_name, date_from, date_to)
    total = db.scalar(select(func.count()).select_from(base_statement.subquery())) or 0
    items = list(
        db.scalars(
            base_statement
            .order_by(*_latest_ordering())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )
    return items, int(total)


def create_inventory_entry(db: Session, payload: InventoryEntryCreate, user: User) -> InventoryEntry:
    entry = InventoryEntry(
        **payload.model_dump(),
        balance_quantity=0,
        created_by=user.name,
    )
    db.add(entry)
    db.flush()
    _recalculate_part_balances(db, entry.part_name)
    db.commit()
    db.refresh(entry)
    return entry


def update_inventory_entry(db: Session, entry_id: int, payload: InventoryEntryUpdate) -> InventoryEntry:
    entry = _get_entry(db, entry_id)
    previous_part_name = entry.part_name

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)

    db.flush()
    _recalculate_part_balances(db, previous_part_name)
    if entry.part_name != previous_part_name:
        _recalculate_part_balances(db, entry.part_name)
    db.commit()
    db.refresh(entry)
    return entry


def delete_inventory_entry(db: Session, entry_id: int) -> None:
    entry = _get_entry(db, entry_id)
    part_name = entry.part_name
    db.delete(entry)
    db.flush()
    _recalculate_part_balances(db, part_name)
    db.commit()


def get_inventory_balance_preview(
    db: Session,
    part_name: str,
    in_quantity: int,
    out_quantity: int,
    rejection_quantity: int,
) -> InventoryBalancePreview:
    previous_entry = db.scalar(
        select(InventoryEntry)
        .where(InventoryEntry.part_name == part_name)
        .order_by(*_latest_ordering())
        .limit(1)
    )
    previous_balance = previous_entry.balance_quantity if previous_entry else 0
    projected_balance = previous_balance + in_quantity - out_quantity - rejection_quantity
    return InventoryBalancePreview(
        part_name=part_name,
        previous_balance=previous_balance,
        projected_balance=projected_balance,
    )


def get_inventory_summary(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> InventorySummaryResponse:
    totals_statement = select(
        func.coalesce(func.sum(InventoryEntry.in_quantity), 0),
        func.coalesce(func.sum(InventoryEntry.out_quantity), 0),
        func.coalesce(func.sum(InventoryEntry.rejection_quantity), 0),
    )
    if date_from:
        totals_statement = totals_statement.where(InventoryEntry.date >= date_from)
    if date_to:
        totals_statement = totals_statement.where(InventoryEntry.date <= date_to)

    totals = db.execute(totals_statement).one()

    part_balances = _build_part_balance_rows(db, date_from, date_to)
    low_inventory_items = [item for item in part_balances if item.is_low_inventory]
    total_inventory = sum(item.balance_quantity for item in part_balances)

    recent_statement = select(InventoryEntry)
    if date_from:
        recent_statement = recent_statement.where(InventoryEntry.date >= date_from)
    if date_to:
        recent_statement = recent_statement.where(InventoryEntry.date <= date_to)
    recent_entries = list(
        db.scalars(recent_statement.order_by(*_latest_ordering()).limit(8)).all()
    )

    movement_statement = (
        select(
            InventoryEntry.date,
            func.coalesce(func.sum(InventoryEntry.in_quantity), 0),
            func.coalesce(func.sum(InventoryEntry.out_quantity), 0),
        )
        .group_by(InventoryEntry.date)
        .order_by(InventoryEntry.date.desc())
    )
    if date_from:
        movement_statement = movement_statement.where(InventoryEntry.date >= date_from)
    if date_to:
        movement_statement = movement_statement.where(InventoryEntry.date <= date_to)

    movement_rows = db.execute(movement_statement.limit(7)).all()

    movement_series = [
        InventoryMovementPoint(
            label=row[0].strftime("%d %b"),
            in_quantity=int(row[1]),
            out_quantity=int(row[2]),
        )
        for row in reversed(movement_rows)
    ]

    return InventorySummaryResponse(
        total_inventory=total_inventory,
        total_in_quantity=int(totals[0]),
        total_out_quantity=int(totals[1]),
        total_rejections=int(totals[2]),
        low_inventory_count=len(low_inventory_items),
        low_inventory_threshold=settings.inventory_low_threshold,
        low_inventory_items=low_inventory_items[:10],
        part_balances=part_balances,
        movement_series=movement_series,
        recent_entries=recent_entries,
    )
