from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas import TokenResponse, UserLoginRequest, UserSignupRequest

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(request: UserSignupRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_username(request.username, db) is not None:
        raise HTTPException(status_code=409, detail="Username already taken")
    user = crud.create_user(request.username, hash_password(request.password), db)
    return TokenResponse(access_token=create_access_token(user.user_id), user=user)


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(request.username, db)
    if user is None or user.password_hash is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return TokenResponse(access_token=create_access_token(user.user_id), user=user)
