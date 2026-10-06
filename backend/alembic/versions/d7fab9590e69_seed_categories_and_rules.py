"""seed category taxonomy and global keyword rules

Revision ID: d7fab9590e69
Revises: a549cbe91d90
Create Date: 2026-10-05

"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.db.types import GUID
from app.services.category_taxonomy import CATEGORIES, KEYWORD_RULES

# revision identifiers, used by Alembic.
revision: str = "d7fab9590e69"
down_revision: Union[str, None] = "a549cbe91d90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    categories_table = sa.table(
        "categories", sa.column("id", GUID()), sa.column("name", sa.String())
    )
    rules_table = sa.table(
        "merchant_category_rules",
        sa.column("id", GUID()),
        sa.column("user_id", GUID()),
        sa.column("keyword", sa.String()),
        sa.column("category_id", GUID()),
    )

    category_ids = {name: uuid.uuid4() for name in CATEGORIES}
    op.bulk_insert(categories_table, [{"id": category_ids[name], "name": name} for name in CATEGORIES])

    op.bulk_insert(
        rules_table,
        [
            {
                "id": uuid.uuid4(),
                "user_id": None,
                "keyword": keyword,
                "category_id": category_ids[category_name],
            }
            for keyword, category_name in KEYWORD_RULES.items()
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM merchant_category_rules WHERE user_id IS NULL")
    op.execute("DELETE FROM categories")
