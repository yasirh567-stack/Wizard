import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


class Category(Base):
    """A fixed taxonomy (WIZ-7), not free text — see SPRINT_2.md.

    The existing `transactions.category` column holds whatever label the
    source (Plaid, a CSV column) gave us; this table is the canonical
    category a transaction is actually bucketed under.
    """

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
