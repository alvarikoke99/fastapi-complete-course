from starlette import status
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import User
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserDto(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    phone_number: str

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

@router.get("/get_user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency) -> UserDto:
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    user_data = db.query(User).filter(User.id == user.get("user_id")).first()

    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return UserDto(email=user_data.email,
                   username=user_data.username,
                   first_name=user_data.first_name,
                   last_name=user_data.last_name,
                   is_active=user_data.is_active,
                   role=user_data.role,
                   phone_number=user_data.phone_number)

@router.post("/change_password", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    user_data = db.query(User).filter(User.id == user.get("user_id")).first()

    if not bcrypt_context.verify(user_verification.password, user_data.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    user_data.hashed_password = bcrypt_context.hash(user_verification.password)

    db.add(user_data)
    db.commit()

@router.put("/phone", status_code=status.HTTP_200_OK)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: str = Body(min_length=9, max_length=9)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

    user_data = db.query(User).filter(User.id == user.get("user_id")).first()
    user_data.phone_number = phone_number

    db.add(user_data)
    db.commit()
