from datetime import datetime, time
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.models.production_entry import ProductionEntry
from app.services.inventory_service import get_inventory_summary
from app.services.production_service import get_machine_analytics
from app.utils.config import settings


def _notification_row(
    row_id: int,
    message: str,
    notification_type: NotificationType,
    created_at: datetime,
    is_read: bool = False,
) -> dict:
    return {
        "id": row_id,
        "message": message,
        "type": notification_type,
        "is_read": is_read,
        "created_at": created_at,
    }


def list_notifications(db: Session) -> list[Any]:
    notifications: list[Any] = []
    now = datetime.utcnow()
    row_id = 1

    inventory_summary = get_inventory_summary(db)
    for item in inventory_summary.low_inventory_items:
        notifications.append(
            _notification_row(
                row_id,
                f"Low inventory: {item.part_name} balance is {item.balance_quantity} below threshold {settings.inventory_low_threshold}.",
                NotificationType.LOW_STOCK,
                datetime.combine(item.latest_entry_date, time.min),
            )
        )
        row_id += 1

    for machine in get_machine_analytics(db):
        if not machine.is_underperforming:
            continue
        notifications.append(
            _notification_row(
                row_id,
                f"Production delay: {machine.machine_number} made {machine.actual_production} against target {machine.daily_target} ({machine.efficiency_percent}%).",
                NotificationType.PRODUCTION_DELAY,
                now,
            )
        )
        row_id += 1

    recent_entries = list(
        db.scalars(select(ProductionEntry).order_by(ProductionEntry.created_at.desc()).limit(5)).all()
    )
    for entry in recent_entries:
        notifications.append(
            _notification_row(
                row_id,
                f"Production updated: {entry.machine_number} saved {entry.actual_production} units for {entry.part_name}.",
                NotificationType.TASK_UPDATE,
                entry.created_at,
                is_read=True,
            )
        )
        row_id += 1

    saved_notifications = list(db.scalars(select(Notification).order_by(Notification.created_at.desc())).all())
    notifications.extend(saved_notifications)
    return sorted(notifications, key=lambda item: item["created_at"] if isinstance(item, dict) else item.created_at, reverse=True)
