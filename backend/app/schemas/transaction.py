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
