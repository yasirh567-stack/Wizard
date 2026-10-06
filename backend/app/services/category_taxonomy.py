"""The fixed v1 category taxonomy and global keyword rules (WIZ-7).

Single source of truth for both the seed migration
(alembic/versions/d7fab9590e69_seed_categories_and_rules.py) and the
categorizer itself, so the two can't drift apart.
"""

from sqlalchemy.orm import Session

UNCATEGORIZED = "Uncategorized"

CATEGORIES = [
    "Income",
    "Transfer",
    "Rent and Utilities",
    "Internet and Cable",
    "Phone",
    "Gyms and Fitness Centers",
    "Entertainment",
    "Groceries",
    "Restaurants",
    "Gas",
    "Shopping",
    UNCATEGORIZED,
]

# Lowercase keyword -> category name. Matched as a case-insensitive
# substring of a transaction's merchant_name/name by the categorizer.
KEYWORD_RULES = {
    "payroll": "Income",
    "employer": "Income",
    "internal transfer": "Transfer",
    "landlord": "Rent and Utilities",
    "rent payment": "Rent and Utilities",
    "comcast": "Internet and Cable",
    "internet bill": "Internet and Cable",
    "verizon": "Phone",
    "phone bill": "Phone",
    "anytime fitness": "Gyms and Fitness Centers",
    "gym membership": "Gyms and Fitness Centers",
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "trader joe": "Groceries",
    "whole foods": "Groceries",
    "safeway": "Groceries",
    "costco": "Groceries",
    "chipotle": "Restaurants",
    "sweetgreen": "Restaurants",
    "local diner": "Restaurants",
    "thai kitchen": "Restaurants",
    "shell": "Gas",
    "chevron": "Gas",
    "amazon": "Shopping",
    "target": "Shopping",
    "best buy": "Shopping",
}


def seed_categories_and_rules(db: Session) -> None:
    """Idempotent. Used by the test fixtures (tests/conftest.py builds
    schema via Base.metadata.create_all, not Alembic, so it needs this to
    get the same taxonomy a real `docker compose up` gets from the
    migration) and safe to call against an already-seeded database.
    """
    # Imported here, not at module scope: avoids a model-import cycle for
    # the one caller (the seed migration) that only needs CATEGORIES/
    # KEYWORD_RULES, not the ORM classes.
    from app.models.category import Category
    from app.models.merchant_category_rule import MerchantCategoryRule

    category_by_name = {}
    for name in CATEGORIES:
        category = db.query(Category).filter(Category.name == name).one_or_none()
        if category is None:
            category = Category(name=name)
            db.add(category)
            db.flush()
        category_by_name[name] = category

    for keyword, category_name in KEYWORD_RULES.items():
        existing = (
            db.query(MerchantCategoryRule)
            .filter(MerchantCategoryRule.user_id.is_(None), MerchantCategoryRule.keyword == keyword)
            .one_or_none()
        )
        if existing is None:
            db.add(
                MerchantCategoryRule(
                    user_id=None, keyword=keyword, category_id=category_by_name[category_name].id
                )
            )

    db.commit()
