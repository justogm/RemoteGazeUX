"""
Repository for Subject entity operations.
"""

from typing import List, Optional
from db.models import Subject
from .base_repository import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    """Repository for managing Subject entities."""

    def __init__(self):
        super().__init__(Subject)

    def create_subject(
        self, name: str, surname: str, age: int, study_id: Optional[int] = None
    ) -> Subject:
        """
        Create a new subject.

        Args:
            name: Subject's name
            surname: Subject's surname
            age: Subject's age
            study_id: Optional ID of the study this subject belongs to

        Returns:
            The created Subject instance
        """
        subject = Subject(name=name, surname=surname, age=age, study_id=study_id)
        self.add(subject)
        return subject

    def get_all_subjects(self) -> List[Subject]:
        """
        Get all subjects.

        Returns:
            List of all subjects
        """
        return self.get_all()

    def get_subject_by_id(self, subject_id: int) -> Optional[Subject]:
        """
        Get a subject by ID.

        Args:
            subject_id: The ID of the subject

        Returns:
            The subject if found, None otherwise
        """
        return self.get_by_id(subject_id)
