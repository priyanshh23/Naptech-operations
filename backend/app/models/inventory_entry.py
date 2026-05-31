from datetime import date as date_type
from datetime import datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class InventoryEntry(Base):
    __tablename__ = "inventory_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[date_type] = mapped_column(Date, index=True, nullable=False)
    part_name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    schedule_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    in_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    out_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejection_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    balance_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
