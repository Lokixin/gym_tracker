import hashlib
import hmac
import logging
import secrets
from datetime import timedelta, datetime, timezone
from typing import Annotated, cast

import jwt
from fastapi import Depends, APIRouter, HTTPException, Response, Cookie, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from gym_tracker.entrypoints.dependencies import get_db_session
from gym_tracker.domain.models.user import User as DBUser

logger = logging.getLogger(__name__)

SECRET_KEY = "29e2c5c487ea5f1d8f12cb320f4f4565d6c568de8308dffc3a21db175ae3d798"
ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

ACCESS_TOKEN_EXPIRE_MINUTES = 30


auth_router = APIRouter(
    prefix="/api/users",
    tags=["users"],
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: EmailStr | None = Field(default=None)
    full_name: str | None = None
    disabled: bool | None = None
    id: int


class UserInDB(User):
    hashed_password: str


class CreateUserRequest(User):
    plain_text_password: str


def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_text_password, hashed_password)


def hash_password(plain_text_password: str) -> str:
    return password_hash.hash(plain_text_password)


def authenticate_user(
    username: str, password: str, db_session: Session
) -> UserInDB | None:
    user = get_user(username, db_session)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    data: dict, session_id: str, expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire_in = datetime.now(timezone.utc) + expires_delta
    else:
        expire_in = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire_in})
    to_encode.update({"jit": session_id})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(username: str | None, db_session: Session) -> UserInDB | None:
    if not username:
        return None
    user_statement = select(DBUser).where(DBUser.username == username)
    user = db_session.scalars(user_statement).one()
    if not user:
        return None
    return UserInDB(
        username=user.username,
        hashed_password=user.password,
        email=user.email,
        id=user.id,
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: Session = Depends(get_db_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, db_session=db_session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_by_cookie(
    auth_jwt: Annotated[str | None, Cookie()] = None,
    x_csrf_token: Annotated[str | None, Header()] = None,
    db_session: Session = Depends(get_db_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        assert auth_jwt
        payload = jwt.decode(auth_jwt, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        session_id = cast(str, payload.get("jit"))
        assert session_id and isinstance(session_id, str)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        if x_csrf_token:
            csrf_token, random_value = x_csrf_token.split(".")
            message = (
                f"{len(session_id)}!{session_id}!{len(random_value)}!{random_value}"
            )
            expected_hmac = hmac.new(
                SECRET_KEY.encode(), message.encode(), digestmod=hashlib.sha256
            )
            does_signature_match = hmac.compare_digest(
                csrf_token, expected_hmac.hexdigest()
            )
            if not does_signature_match:
                raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, db_session=db_session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@auth_router.post("/token")
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Session = Depends(get_db_session),
):
    user = authenticate_user(form_data.username, form_data.password, db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    session_id = secrets.token_urlsafe(32)
    random_value = secrets.token_hex(64)
    message = f"{len(session_id)}!{session_id}!{len(random_value)}!{random_value}"
    hmac_message = hmac.new(
        SECRET_KEY.encode(), message.encode(), digestmod=hashlib.sha256
    )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
        session_id=session_id,
    )
    csrf_token = hmac_message.hexdigest() + "." + random_value
    response.set_cookie(key="auth_jwt", value=access_token)
    response.set_cookie(key="csrf_token", value=csrf_token, httponly=False)
    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@auth_router.post("")
async def register_user(
    new_user: CreateUserRequest, db_session: Session = Depends(get_db_session)
) -> User:
    hashed_password = hash_password(new_user.plain_text_password)
    user = DBUser(
        username=new_user.username, password=hashed_password, email=str(new_user.email)
    )
    try:
        db_session.add(user)
        db_session.commit()
    except IntegrityError as e:
        logger.error(e)
        error_msg = (
            f"username: {new_user.username} already exists"
            if "(username)=" in str(e)
            else f"email: {new_user.email} already exists"
        )
        raise HTTPException(status_code=400, detail=error_msg) from e

    return User(id=user.id, username=new_user.username, email=new_user.email)
