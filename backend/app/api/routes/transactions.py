import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.csv_upload import CsvUploadResponse
from app.schemas.transaction import TransactionRead
from app.services.csv_import import CsvFormatError, import_csv

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    account_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Transaction]:
    stmt = (
        select(Transaction)
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.user_id == current_user.id)
        .order_by(Transaction.date.desc())
    )
    if account_id is not None:
        stmt = stmt.where(Account.id == account_id)
    return list(db.scalars(stmt).all())


@router.post("/csv-upload", response_model=CsvUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(...),
    account_id: uuid.UUID | None = Form(default=None),
    account_name: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CsvUploadResponse:
    if account_id is not None:
        account = db.scalar(
            select(Account).where(Account.id == account_id, Account.user_id == current_user.id)
        )
        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    else:
        account = Account(user_id=current_user.id, source="csv", name=account_name or "CSV Import")
        db.add(account)
        db.flush()

    raw_bytes = await file.read()
    try:
        csv_text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="file must be UTF-8 encoded CSV"
        ) from exc

    try:
        result = import_csv(db, account, csv_text)
    except CsvFormatError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.commit()

    return CsvUploadResponse(
        account_id=account.id,
        imported=result.imported,
        skipped=result.skipped,
        errors=[{"row": e.row, "reason": e.reason} for e in result.errors],
    )
