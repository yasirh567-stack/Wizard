from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.demo import DemoLoadResponse
from app.services.demo_seed import generate_demo_data

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/load", response_model=DemoLoadResponse, status_code=status.HTTP_201_CREATED)
def load_demo_data(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> dict[str, int]:
    return generate_demo_data(db, current_user)
