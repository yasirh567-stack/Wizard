import uuid
from datetime import date as date_
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # WIZ-5 dedup keys: the Plaid path keys off plaid_transaction_id; the
    # CSV/demo path keys off a content hash of date+amount+merchant+account.
    # Exactly one is set per row depending on source.
    plaid_transaction_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)

    # WIZ-6: when a pending transaction posts, Plaid assigns it a new
    # transaction_id and links back to the pending one via this field — used
    # to update the existing row in place instead of inserting a duplicate.
    pending_transaction_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    date: Mapped[date_] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    merchant_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    account: Mapped["Account"] = relationship(back_populates="transactions")
