from pydantic import BaseModel


class DemoLoadResponse(BaseModel):
    accounts_created: int
    transactions_created: int
