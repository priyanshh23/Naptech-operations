from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.production_entry import ProductionEntry
from app.models.user import User
from app.schemas.production import (
    MachineAnalyticsRow,
    ProductionChartPoint,
    ProductionEntryCreate,
    ProductionEntryResponse,
    ProductionEntryUpdate,
    ProductionSummaryResponse,
)


def _latest_ordering():
    return ProductionEntry.date.desc(), ProductionEntry.created_at.desc(), ProductionEntry.id.desc()


def _efficiency(actual_production: int, daily_target: int) -> float:
    if daily_target <= 0:
        return 0
    return round((actual_production / daily_target) * 100, 1)


def _to_response(entry: ProductionEntry) -> ProductionEntryResponse:
    return ProductionEntryResponse.model_validate(
        {
            **entry.__dict__,
            "efficiency_percent": _efficiency(entry.actual_production, entry.daily_target),
        }
    )


def _query_entries(
    search: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    statement = select(ProductionEntry)

    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                ProductionEntry.machine_number.ilike(pattern),
                ProductionEntry.operator_name.ilike(pattern),
                ProductionEntry.part_number.ilike(pattern),
                ProductionEntry.part_name.ilike(pattern),
                ProductionEntry.remarks.ilike(pattern),
            )
        )
    if date_from:
        statement = statement.where(ProductionEntry.date >= date_from)
    if date_to:
        statement = statement.where(ProductionEntry.date <= date_to)

    return statement


def create_production_entry(db: Session, payload: ProductionEntryCreate, user: User) -> ProductionEntryResponse:
    entry = ProductionEntry(**payload.model_dump(), created_by=user.name)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _to_response(entry)


def create_production_entries(
    db: Session,
    payloads: list[ProductionEntryCreate],
    user: User,
) -> list[ProductionEntryResponse]:
    entries = [ProductionEntry(**payload.model_dump(), created_by=user.name) for payload in payloads]
    db.add_all(entries)
    db.commit()
    for entry in entries:
        db.refresh(entry)
    return [_to_response(entry) for entry in entries]


def update_production_entry(db: Session, entry_id: int, payload: ProductionEntryUpdate) -> ProductionEntryResponse:
    entry = db.get(ProductionEntry, entry_id)
    if not entry:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production entry not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)
    return _to_response(entry)


def delete_production_entry(db: Session, entry_id: int) -> None:
    entry = db.get(ProductionEntry, entry_id)
    if not entry:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production entry not found")

    db.delete(entry)
    db.commit()


def list_production_entries(
    db: Session,
    search: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> tuple[list[ProductionEntryResponse], int]:
    base_statement = _query_entries(search, date_from, date_to)
    total = db.scalar(select(func.count()).select_from(base_statement.subquery())) or 0
    entries = list(db.scalars(base_statement.order_by(*_latest_ordering()).limit(100)).all())
    return [_to_response(entry) for entry in entries], int(total)


def get_machine_analytics(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list[MachineAnalyticsRow]:
    statement = select(
        ProductionEntry.machine_number,
        func.coalesce(func.sum(ProductionEntry.daily_target), 0),
        func.coalesce(func.sum(ProductionEntry.actual_production), 0),
    ).group_by(ProductionEntry.machine_number)

    if date_from:
        statement = statement.where(ProductionEntry.date >= date_from)
    if date_to:
        statement = statement.where(ProductionEntry.date <= date_to)

    rows: list[MachineAnalyticsRow] = []
    for machine_number, target, actual in db.execute(statement).all():
        target_value = int(target)
        actual_value = int(actual)
        efficiency = _efficiency(actual_value, target_value)
        rows.append(
            MachineAnalyticsRow(
                machine_number=machine_number,
                daily_target=target_value,
                actual_production=actual_value,
                efficiency_percent=efficiency,
                is_underperforming=actual_value < target_value,
            )
        )

    return sorted(rows, key=lambda row: row.efficiency_percent, reverse=True)


def get_production_summary(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> ProductionSummaryResponse:
    analytics = get_machine_analytics(db, date_from, date_to)
    total_actual = sum(row.actual_production for row in analytics)
    total_target = sum(row.daily_target for row in analytics)
    average_efficiency = _efficiency(total_actual, total_target)
    best_machine = analytics[0].machine_number if analytics else None
    underperforming = len([row for row in analytics if row.is_underperforming])

    date_statement = select(
        ProductionEntry.date,
        func.coalesce(func.sum(ProductionEntry.daily_target), 0),
        func.coalesce(func.sum(ProductionEntry.actual_production), 0),
    ).group_by(ProductionEntry.date).order_by(ProductionEntry.date.asc())
    if date_from:
        date_statement = date_statement.where(ProductionEntry.date >= date_from)
    if date_to:
        date_statement = date_statement.where(ProductionEntry.date <= date_to)

    production_vs_target = [
        ProductionChartPoint(
            label=row_date.strftime("%d/%m"),
            target=int(target),
            actual=int(actual),
        )
        for row_date, target, actual in db.execute(date_statement).all()
    ]

    machine_wise = [
        ProductionChartPoint(
            label=row.machine_number,
            target=row.daily_target,
            actual=row.actual_production,
        )
        for row in analytics
    ]

    recent_entries, _ = list_production_entries(db, date_from=date_from, date_to=date_to)
    return ProductionSummaryResponse(
        total_daily_production=total_actual,
        average_machine_efficiency=average_efficiency,
        best_performing_machine=best_machine,
        underperforming_machines=underperforming,
        production_vs_target=production_vs_target[-7:],
        machine_wise_production=machine_wise,
        recent_entries=recent_entries[:8],
    )


def seed_demo_production_entries(db: Session) -> None:
    existing_count = db.scalar(select(func.count(ProductionEntry.id))) or 0
    if existing_count:
        return

    today = date.today()
    demo_rows = [
        ("A", "CNC-01", "Rahul", "TA-204", "Torque Arm", 42, 86, 688, 670, "Stable output"),
        ("A", "CNC-02", "Aman", "GH-118", "Gear Housing", 55, 65, 520, 438, "Tool setting delay"),
        ("A", "VMC-01", "Vishal", "HC-331", "HD Clamp", 38, 94, 752, 790, "Ahead of target"),
        ("B", "VMC-02", "Sandeep", "BP-422", "Bushing Pin", 47, 76, 608, 552, "Material waiting"),
        ("B", "CNC-03", "Rahul", "RH-510", "Rotor Hub", 60, 58, 464, 471, "Normal"),
        ("B", "VMC-03", "Aman", "TA-204", "Torque Arm", 44, 82, 656, 602, "Minor rejection hold"),
        ("C", "CNC-04", "Vishal", "GH-118", "Gear Housing", 52, 69, 552, 575, "Recovered after lunch"),
        ("C", "VMC-04", "Sandeep", "HC-331", "HD Clamp", 40, 90, 720, 648, "Inspection delay"),
    ]

    entries: list[ProductionEntry] = []
    for offset in range(3):
        row_date = today - timedelta(days=offset)
        for shift, machine, operator, part_no, part_name, cycle, tph, target, actual, remarks in demo_rows:
            daily_adjustment = offset * 18
            entries.append(
                ProductionEntry(
                    date=row_date,
                    shift=shift,
                    machine_number=machine,
                    operator_name=operator,
                    part_number=part_no,
                    part_name=part_name,
                    cycle_time_seconds=cycle,
                    target_per_hour=tph,
                    daily_target=target,
                    actual_production=max(0, actual - daily_adjustment),
                    remarks=remarks,
                    created_by="Supervisor",
                )
            )

    db.add_all(entries)
    db.commit()
