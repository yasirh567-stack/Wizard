from fastapi import APIRouter, Depends, HTTPException, status
from plaid.exceptions import ApiException
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.encryption import encrypt
from app.db.session import get_db
from app.models.account import Account
from app.models.plaid_item import PlaidItem
from app.models.user import User
from app.schemas.plaid import (
    LinkTokenResponse,
    PublicTokenExchangeRequest,
    PublicTokenExchangeResponse,
    SyncResult,
)
from app.services.plaid_client import get_plaid_client
from app.services.plaid_sync import sync_transactions

router = APIRouter(prefix="/plaid", tags=["plaid"])


@router.post("/link-token", response_model=LinkTokenResponse)
def create_link_token(current_user: User = Depends(get_current_user)) -> LinkTokenResponse:
    client = get_plaid_client()
    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=str(current_user.id)),
        client_name="Wizard",
        products=[Products("transactions")],
        country_codes=[CountryCode("US")],
        language="en",
    )
    try:
        response = client.link_token_create(request)
    except ApiException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Plaid link token creation failed"
        ) from exc

    return LinkTokenResponse(link_token=response.link_token)


@router.post(
    "/exchange-public-token",
    response_model=PublicTokenExchangeResponse,
    status_code=status.HTTP_201_CREATED,
)
def exchange_public_token(
    payload: PublicTokenExchangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PublicTokenExchangeResponse:
    client = get_plaid_client()

    try:
        exchange_response = client.item_public_token_exchange(
            ItemPublicTokenExchangeRequest(public_token=payload.public_token)
        )
    except ApiException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Plaid token exchange failed"
        ) from exc

    access_token = exchange_response.access_token

    item = PlaidItem(
        user_id=current_user.id,
        plaid_item_id=exchange_response.item_id,
        access_token_encrypted=encrypt(access_token),
    )
    db.add(item)
    db.flush()  # assigns item.id, needed below before accounts reference it

    try:
        accounts_response = client.accounts_get(AccountsGetRequest(access_token=access_token))
    except ApiException as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail="Plaid account fetch failed"
        ) from exc

    item.institution_id = accounts_response.item.institution_id

    accounts_synced = 0
    for plaid_account in accounts_response.accounts:
        db.add(
            Account(
                user_id=current_user.id,
                plaid_item_id=item.id,
                plaid_account_id=plaid_account.account_id,
                source="plaid",
                name=plaid_account.name,
                official_name=plaid_account.official_name,
                type=str(plaid_account.type),
                subtype=str(plaid_account.subtype) if plaid_account.subtype else None,
                mask=plaid_account.mask,
            )
        )
        accounts_synced += 1

    db.commit()
    db.refresh(item)

    sync_result = sync_transactions(db, client, item)

    return PublicTokenExchangeResponse(
        item_id=item.plaid_item_id,
        accounts_synced=accounts_synced,
        transactions_synced=sync_result["added"],
    )


@router.post("/sync/{item_id}", response_model=SyncResult)
def resync(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    item = db.scalar(
        select(PlaidItem).where(
            PlaidItem.plaid_item_id == item_id, PlaidItem.user_id == current_user.id
        )
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plaid item not found")

    client = get_plaid_client()
    return sync_transactions(db, client, item)
