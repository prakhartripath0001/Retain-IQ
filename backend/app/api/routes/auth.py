from datetime import timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.security import (
    ACCESS_TOKEN_MINUTES,
    create_access_token,
    decode_access_token,
)
from app.models.user import RevokedToken
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse
from app.services.auth import (
    AuthService,
    DuplicateEmailError,
    InactiveUserError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
service = AuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: RegisterRequest, db: DbSession):
    try:
        return service.register(db, data)
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    db: DbSession,
):
    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email_or_username = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        try:
            body = await request.json()
            email_or_username = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid request body",
            )

    if not email_or_username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email/username and password are required",
        )

    try:
        user = service.authenticate(db, str(email_or_username), str(password))
    except (InvalidCredentialsError, InactiveUserError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password, or inactive account",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    token, _, _ = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        expires_in=ACCESS_TOKEN_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: CurrentUser,
    db: DbSession,
    token: Annotated[
        str,
        Depends(
            __import__("fastapi.security", fromlist=["OAuth2PasswordBearer"]).OAuth2PasswordBearer(
                tokenUrl="/api/v1/auth/login"
            )
        ),
    ],
):
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from exc

    token_id = payload["jti"]
    expires_at = payload["exp"]

    if db.get(RevokedToken, token_id) is None:
        db.add(
            RevokedToken(
                jti=token_id,
                expires_at=__import__("datetime").datetime.fromtimestamp(
                    expires_at, tz=timezone.utc
                ).replace(tzinfo=None),
            )
        )
        db.commit()

    return None