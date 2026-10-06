import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import GUID


class MerchantCategoryRule(Base):
    """A keyword -> category mapping used by the rule-seeded categorizer.

    user_id NULL: a global seed rule (WIZ-7) — `keyword` is matched as a
    case-insensitive substring of the transaction's merchant_name/name.

    user_id set: a per-user override written by a manual correction
    (WIZ-9) — `keyword` is the merchant_name itself (exact, lowercased),
    checked before any global rule so a user's own correction always wins.
    """

    __tablename__ = "merchant_category_rules"
    __table_args__ = (
        UniqueConstraint("user_id", "keyword", name="uq_merchant_category_rules_user_keyword"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
