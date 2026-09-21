from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountRead

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountRead])
def list_accounts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Account]:
    stmt = select(Account).where(Account.user_id == current_user.id).order_by(Account.created_at)
    return list(db.scalars(stmt).all())
