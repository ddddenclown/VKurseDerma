from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer

from schemas.user import UserCreate, UserRead
from crud.user import create_user, get_user_by_username, get_user_by_email
from core.database import get_async_session
from core.security import create_access_token, get_current_user
from core.utils import verify_password
from models.user import User
from schemas.user import UserRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_async_session),
):
    existing_user = await get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing_email = await get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await create_user(db, user_in)
    return user

@router.post("/login")
async def login(
        db: AsyncSession = Depends(get_async_session),
        username: str = Form(...),
        password: str = Form(...),
):
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "user_id": user.id,
        "username": user.username,
    }

@router.get("/me", response_model=UserRead)
async def read_me(
        current_user: User = Depends(get_current_user)
):
    return current_user