"""categorization, recurring detection, anomaly detection

Revision ID: a549cbe91d90
Revises: 5e6455f27ddb
Create Date: 2026-10-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.db.types import GUID

# revision identifiers, used by Alembic.
revision: str = "a549cbe91d90"
down_revision: Union[str, None] = "5e6455f27ddb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    op.create_table(
        "merchant_category_rules",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "user_id", GUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True
        ),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column(
            "category_id",
            GUID(),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "keyword", name="uq_merchant_category_rules_user_keyword"),
    )
    op.create_index(
        "ix_merchant_category_rules_user_id", "merchant_category_rules", ["user_id"]
    )

    op.create_table(
        "recurring_series",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "account_id", GUID(), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("merchant_name", sa.String(length=255), nullable=False),
        sa.Column("expected_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("expected_interval_days", sa.Integer(), nullable=False),
        sa.Column("last_seen_date", sa.Date(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_recurring_series_account_id", "recurring_series", ["account_id"])

    op.create_table(
        "anomaly_flags",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "transaction_id",
            GUID(),
            sa.ForeignKey("transactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=50), nullable=False),
        sa.Column("detail", sa.String(length=255), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("transaction_id", name="uq_anomaly_flags_transaction_id"),
    )

    # batch_alter_table: SQLite can't ALTER TABLE ADD COLUMN with an inline
    # FK constraint directly (it recreates the table instead); on Postgres
    # this just emits plain ALTER statements. Needed for the GUID()-backed
    # test path (tests/conftest.py), not only Postgres.
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.add_column(
            sa.Column(
                "category_id",
                GUID(),
                sa.ForeignKey(
                    "categories.id", ondelete="SET NULL", name="fk_transactions_category_id"
                ),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("category_confidence", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("category_source", sa.String(length=20), nullable=True))
        batch_op.add_column(
            sa.Column(
                "recurring_series_id",
                GUID(),
                sa.ForeignKey(
                    "recurring_series.id",
                    ondelete="SET NULL",
                    name="fk_transactions_recurring_series_id",
                ),
                nullable=True,
            )
        )

    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_recurring_series_id", "transactions", ["recurring_series_id"])


def downgrade() -> None:
    op.drop_index("ix_transactions_recurring_series_id", table_name="transactions")
    op.drop_index("ix_transactions_category_id", table_name="transactions")

    with op.batch_alter_table("transactions") as batch_op:
        batch_op.drop_column("recurring_series_id")
        batch_op.drop_column("category_source")
        batch_op.drop_column("category_confidence")
        batch_op.drop_column("category_id")

    op.drop_table("anomaly_flags")
    op.drop_table("recurring_series")
    op.drop_table("merchant_category_rules")
    op.drop_table("categories")
