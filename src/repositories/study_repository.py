"""Repository for Study model operations."""

from typing import List, Optional
from datetime import datetime
from db.models import Study, db
from .base_repository import BaseRepository


class StudyRepository(BaseRepository[Study]):
    """Repository for managing Study entities."""

    def __init__(self):
        super().__init__(Study)

    def create_study(
        self,
        name: str,
        description: Optional[str] = None,
        prototype_url: Optional[str] = None,
        prototype_image_path: Optional[str] = None,
    ) -> Study:
        """
        Create a new study.

        Args:
            name: Name of the study
            description: Optional description of the study
            prototype_url: URL to the prototype (Figma, etc.)
            prototype_image_path: Path to a static image prototype

        Returns:
            Created Study instance
        """
        study = Study(
            name=name,
            description=description,
            prototype_url=prototype_url,
            prototype_image_path=prototype_image_path,
            created_at=datetime.now(),
        )
        db.session.add(study)
        db.session.commit()
        return study

    def get_all_studies(self) -> List[Study]:
        """Get all studies ordered by creation date (newest first)."""
        return Study.query.order_by(Study.created_at.desc()).all()

    def get_study_by_id(self, study_id: int) -> Optional[Study]:
        """Get a study by its ID."""
        return Study.query.get(study_id)

    def get_study_by_name(self, name: str) -> Optional[Study]:
        """Get a study by its name."""
        return Study.query.filter_by(name=name).first()

    def update_study(
        self,
        study_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        prototype_url: Optional[str] = None,
        prototype_image_path: Optional[str] = None,
    ) -> Optional[Study]:
        """
        Update an existing study.

        Args:
            study_id: ID of the study to update
            name: New name (if provided)
            description: New description (if provided)
            prototype_url: New prototype URL (if provided)
            prototype_image_path: New image path (if provided)

        Returns:
            Updated Study instance or None if not found
        """
        study = self.get_study_by_id(study_id)
        if not study:
            return None

        if name is not None:
            study.name = name
        if description is not None:
            study.description = description
        if prototype_url is not None:
            study.prototype_url = prototype_url
        if prototype_image_path is not None:
            study.prototype_image_path = prototype_image_path

        db.session.commit()
        return study

    def delete_study(self, study_id: int) -> bool:
        """
        Delete a study by its ID.

        Args:
            study_id: ID of the study to delete

        Returns:
            True if deleted, False if not found
        """
        study = self.get_study_by_id(study_id)
        if not study:
            return False

        db.session.delete(study)
        db.session.commit()
        return True

    def get_active_study(self) -> Optional[Study]:
        """
        Get the most recently created study (assumed to be the active one).

        Returns:
            Most recent Study or None if no studies exist
        """
        return Study.query.order_by(Study.created_at.desc()).first()
