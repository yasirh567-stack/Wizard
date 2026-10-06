import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: uuid.UUID
    date: date
    amount: Decimal
    merchant_name: str | None
    name: str
    category: str | None
    pending: bool

    # WIZ-7/8: the canonical category a detector or correction assigned.
    # Resolve to a name via GET /categories. None only before any detector
    # has run (should not happen for any transaction that went through an
    # ingestion path, which categorizes synchronously on insert).
    category_id: uuid.UUID | None
    category_confidence: float | None
    category_source: str | None
