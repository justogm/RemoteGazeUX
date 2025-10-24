"""
Repository for Measurement entity operations.
"""

from typing import List, Optional
from datetime import datetime
from db.models import Measurement, Point
from .base_repository import BaseRepository


class MeasurementRepository(BaseRepository[Measurement]):
    """Repository for managing Measurement entities."""

    def __init__(self):
        super().__init__(Measurement)

    def create_measurement(
        self,
        date: datetime,
        subject_id: int,
        mouse_point: Optional[Point] = None,
        gaze_point: Optional[Point] = None,
    ) -> Measurement:
        """
        Create a new measurement.

        Args:
            date: The date/time of the measurement
            subject_id: The ID of the subject
            mouse_point: The mouse point (optional)
            gaze_point: The gaze point (optional)

        Returns:
            The created Measurement instance
        """
        measurement = Measurement(
            date=date,
            subject_id=subject_id,
            mouse_point=mouse_point,
            gaze_point=gaze_point,
        )
        self.add(measurement)
        return measurement

    def get_measurements_by_subject(self, subject_id: int) -> List[Measurement]:
        """
        Get all measurements for a specific subject.

        Args:
            subject_id: The ID of the subject

        Returns:
            List of measurements
        """
        return self.model.query.filter_by(subject_id=subject_id).all()

    def count_measurements_by_subject(self, subject_id: int) -> int:
        """
        Count measurements for a specific subject.

        Args:
            subject_id: The ID of the subject

        Returns:
            Number of measurements
        """
        return self.model.query.filter_by(subject_id=subject_id).count()
