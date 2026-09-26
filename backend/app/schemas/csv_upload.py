import uuid

from pydantic import BaseModel


class CsvRowError(BaseModel):
    row: int
    reason: str


class CsvUploadResponse(BaseModel):
    account_id: uuid.UUID
    imported: int
    skipped: int
    errors: list[CsvRowError]
