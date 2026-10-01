
from datetime import timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class AuthService:
    def register(self, db: Session, data: RegisterRequest) -> User:
        email = str(data.email).lower()

        existing = db.scalar(
            select(User).where(User.email == email)
        )
        if existing:
            raise DuplicateEmailError("Email is already registered")

        user = User(
            name=data.name.strip(),
            email=email,
            password_hash=hash_password(data.password),
            role="ANALYST",
            is_active=True,
        )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError as exc:
            db.rollback()
            raise DuplicateEmailError(
                "Email is already registered"
            ) from exc

    def authenticate(
        self, db: Session, email: str, password: str
    ) -> User:
        user = db.scalar(
            select(User).where(User.email == email.lower())
        )

        if user is None:
            # Perform a hash verification even for unknown emails.
            # This reduces, but does not eliminate, timing differences.
            verify_password(password, self.dummy_hash)
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InactiveUserError("Account is inactive")

        return user

    @property
    def dummy_hash(self):
        if not hasattr(self, "_dummy_hash"):
            self._dummy_hash = hash_password(
                "dummy-password-not-used-for-login"
            )
        return self._dummy_hash