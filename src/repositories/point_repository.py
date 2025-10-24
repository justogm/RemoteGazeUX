"""
Repository for Point entity operations.
"""

from typing import List
from db.models import Point
from .base_repository import BaseRepository


class PointRepository(BaseRepository[Point]):
    """Repository for managing Point entities."""

    def __init__(self):
        super().__init__(Point)

    def create_point(self, x: float, y: float) -> Point:
        """
        Create a new point.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            The created Point instance
        """
        point = Point(x=x, y=y)
        self.add(point)
        return point

    def get_points_by_subject(self, subject_id: int) -> List[Point]:
        """
        Get all points for a specific subject (via measurements).

        Args:
            subject_id: The ID of the subject

        Returns:
            List of points
        """
        # Note: This requires joining with Measurement table
        # Implementation would depend on specific query needs
        return self.model.query.filter_by(subject_id=subject_id).all()
