from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Imported so Base.metadata is complete for Alembic autogenerate and
# for create_all in tests — not used directly.
from app.models import account, plaid_item, transaction, user  # noqa: E402,F401
