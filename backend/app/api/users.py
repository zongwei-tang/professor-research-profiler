from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.schemas import UserLoginRequest, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/login", response_model=UserResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    return crud.get_or_create_user(request.username, db)
