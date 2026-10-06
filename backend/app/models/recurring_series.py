import uuid
from datetime import date as date_
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


class RecurringSeries(Base):
    """A detected recurring charge (WIZ-10): same account + merchant,
    repeating at a roughly-consistent interval and amount — not
    necessarily an exact 30-day gap.
    """

    __tablename__ = "recurring_series"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    merchant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    expected_interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    last_seen_date: Mapped[date_] = mapped_column(Date, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
