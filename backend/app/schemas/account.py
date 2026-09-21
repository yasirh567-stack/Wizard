import uuid

from pydantic import BaseModel, ConfigDict


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    official_name: str | None
    type: str | None
    subtype: str | None
    mask: str | None
    source: str
