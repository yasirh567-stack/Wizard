import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plaid_item_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("plaid_items.id", ondelete="CASCADE"), nullable=True, index=True
    )
    plaid_account_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # "plaid" | "csv" | "demo" — WIZ-2 / WIZ-3 / WIZ-4 share this table.
    source: Mapped[str] = mapped_column(String(20), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    official_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subtype: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mask: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="accounts")
    plaid_item: Mapped["PlaidItem | None"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
