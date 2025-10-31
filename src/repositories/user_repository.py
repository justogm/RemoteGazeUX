"""Repository for User model operations."""

from datetime import datetime
from db.models import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository for managing User entities."""

    def __init__(self):
        super().__init__(User)

    def get_user_by_username(self, username: str) -> User | None:
        """Get a user by username."""
        return User.query.filter_by(username=username).first()

    def create_user(self, username: str, password: str) -> User:
        """Create a new user with hashed password."""
        user = User(username=username, created_at=datetime.now())
        user.set_password(password)
        self.add(user)
        return user

    def get_all_users(self) -> list[User]:
        """Get all users."""
        return User.query.all()

    def user_exists(self, username: str) -> bool:
        """Check if a user exists by username."""
        return User.query.filter_by(username=username).first() is not None
