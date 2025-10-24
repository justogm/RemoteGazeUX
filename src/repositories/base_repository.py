"""
Base repository class providing common database operations.
"""

from typing import Type, TypeVar, Generic, List, Optional
from db.models import db

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: Type[T]):
        """
        Initialize repository with a model class.

        Args:
            model: The SQLAlchemy model class
        """
        self.model = model

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get an entity by its ID.

        Args:
            entity_id: The ID of the entity

        Returns:
            The entity if found, None otherwise
        """
        return self.model.query.filter_by(id=entity_id).first()

    def get_all(self) -> List[T]:
        """
        Get all entities.

        Returns:
            List of all entities
        """
        return self.model.query.all()

    def add(self, entity: T) -> T:
        """
        Add a new entity to the database.

        Args:
            entity: The entity to add

        Returns:
            The added entity
        """
        db.session.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        """
        Delete an entity from the database.

        Args:
            entity: The entity to delete
        """
        db.session.delete(entity)

    def commit(self) -> None:
        """Commit the current transaction."""
        db.session.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        db.session.rollback()
