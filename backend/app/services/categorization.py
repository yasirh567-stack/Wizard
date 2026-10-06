"""WIZ-7/8/9: rule-seeded categorization with confidence and overrides.

Match order for a transaction:
  1. A per-user rule (an exact, lowercased merchant_name match) written by
     a previous manual correction for this user — WIZ-9. High confidence.
  2. A global keyword rule (case-insensitive substring of merchant_name or
     name) — WIZ-7. High confidence.
  3. Fallback to the "Uncategorized" category — low confidence. Still a
     real category_id, never NULL: "I never start from an uncategorized
     list" means the field is always populated, not that everything
     matches.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.merchant_category_rule import MerchantCategoryRule
from app.models.transaction import Transaction
from app.services.category_taxonomy import UNCATEGORIZED

RULE_CONFIDENCE = 0.9
MANUAL_CONFIDENCE = 1.0
UNCATEGORIZED_CONFIDENCE = 0.1

SOURCE_RULE = "rule"
SOURCE_MANUAL = "manual"
SOURCE_UNCATEGORIZED = "uncategorized"


def _get_or_create_category(db: Session, name: str) -> Category:
    category = db.scalar(select(Category).where(Category.name == name))
    if category is None:
        category = Category(name=name)
        db.add(category)
        db.flush()
    return category


def categorize_transaction(db: Session, transaction: Transaction, user_id: uuid.UUID) -> None:
    """Assigns category_id/category_confidence/category_source in place.

    Does not commit — callers (ingestion paths, the correction endpoint)
    control the transaction boundary.
    """
    merchant = (transaction.merchant_name or "").strip().lower()

    if merchant:
        user_rule = db.scalar(
            select(MerchantCategoryRule).where(
                MerchantCategoryRule.user_id == user_id, MerchantCategoryRule.keyword == merchant
            )
        )
        if user_rule is not None:
            transaction.category_id = user_rule.category_id
            transaction.category_confidence = MANUAL_CONFIDENCE
            transaction.category_source = SOURCE_MANUAL
            return

    haystack = f"{transaction.merchant_name or ''} {transaction.name}".lower()
    global_rules = db.scalars(
        select(MerchantCategoryRule).where(MerchantCategoryRule.user_id.is_(None))
    )
    for rule in global_rules:
        if rule.keyword in haystack:
            transaction.category_id = rule.category_id
            transaction.category_confidence = RULE_CONFIDENCE
            transaction.category_source = SOURCE_RULE
            return

    uncategorized = _get_or_create_category(db, UNCATEGORIZED)
    transaction.category_id = uncategorized.id
    transaction.category_confidence = UNCATEGORIZED_CONFIDENCE
    transaction.category_source = SOURCE_UNCATEGORIZED


def correct_category(
    db: Session, transaction: Transaction, user_id: uuid.UUID, category: Category
) -> None:
    """WIZ-8 manual override + WIZ-9 propagation to future transactions
    from the same merchant for this user.
    """
    transaction.category_id = category.id
    transaction.category_confidence = MANUAL_CONFIDENCE
    transaction.category_source = SOURCE_MANUAL

    merchant = (transaction.merchant_name or "").strip().lower()
    if not merchant:
        return

    existing_rule = db.scalar(
        select(MerchantCategoryRule).where(
            MerchantCategoryRule.user_id == user_id, MerchantCategoryRule.keyword == merchant
        )
    )
    if existing_rule is not None:
        existing_rule.category_id = category.id
    else:
        db.add(MerchantCategoryRule(user_id=user_id, keyword=merchant, category_id=category.id))
