import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID


class PlaidItem(Base):
    """A Plaid Item — one bank login, which can cover multiple accounts."""

    __tablename__ = "plaid_items"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plaid_item_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Never logged or returned by any API response — see ARCHITECTURE.md.
    access_token_encrypted: Mapped[str] = mapped_column(String(512), nullable=False)

    institution_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # /transactions/sync cursor (WIZ-5/WIZ-6): re-syncing with an unchanged
    # cursor returns nothing, which is what makes a repeat sync a no-op.
    cursor: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="plaid_items")
    accounts: Mapped[list["Account"]] = relationship(
        back_populates="plaid_item", cascade="all, delete-orphan"
    )
