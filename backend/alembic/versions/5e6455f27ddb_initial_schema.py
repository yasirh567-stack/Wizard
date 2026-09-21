"""initial schema

Revision ID: 5e6455f27ddb
Revises:
Create Date: 2026-09-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "5e6455f27ddb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "plaid_items",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "user_id", GUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("plaid_item_id", sa.String(length=255), nullable=False),
        sa.Column("access_token_encrypted", sa.String(length=512), nullable=False),
        sa.Column("institution_id", sa.String(length=255), nullable=True),
        sa.Column("cursor", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_plaid_items_user_id", "plaid_items", ["user_id"])
    op.create_index("ix_plaid_items_plaid_item_id", "plaid_items", ["plaid_item_id"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "user_id", GUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "plaid_item_id",
            GUID(),
            sa.ForeignKey("plaid_items.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("plaid_account_id", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("official_name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("subtype", sa.String(length=50), nullable=True),
        sa.Column("mask", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_accounts_user_id", "accounts", ["user_id"])
    op.create_index("ix_accounts_plaid_item_id", "accounts", ["plaid_item_id"])
    op.create_index(
        "ix_accounts_plaid_account_id", "accounts", ["plaid_account_id"], unique=True
    )

    op.create_table(
        "transactions",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "account_id", GUID(), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("plaid_transaction_id", sa.String(length=255), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("pending_transaction_id", sa.String(length=255), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("merchant_name", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("pending", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_transactions_account_id", "transactions", ["account_id"])
    op.create_index(
        "ix_transactions_plaid_transaction_id",
        "transactions",
        ["plaid_transaction_id"],
        unique=True,
    )
    op.create_index(
        "ix_transactions_content_hash", "transactions", ["content_hash"], unique=True
    )
    op.create_index(
        "ix_transactions_pending_transaction_id", "transactions", ["pending_transaction_id"]
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("accounts")
    op.drop_table("plaid_items")
    op.drop_table("users")
