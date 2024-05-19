from datetime import datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import config as config
from db.crud import UserRepository
from models.user import User
from schemas.user_schema import UserAuth, UserCreate
from security.pwdcrypt import verify_password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await UserRepository.get_user(session, username)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(user: User):
    to_encode = {"sub": user.username}
    expire = datetime.now() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


# Функция получения User'а по токену
def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return UserAuth(
            username=payload.get("sub"),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
