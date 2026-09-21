from pydantic import BaseModel


class LinkTokenResponse(BaseModel):
    link_token: str


class PublicTokenExchangeRequest(BaseModel):
    public_token: str


class PublicTokenExchangeResponse(BaseModel):
    item_id: str
    accounts_synced: int
    transactions_synced: int


class SyncResult(BaseModel):
    added: int
    modified: int
    removed: int
