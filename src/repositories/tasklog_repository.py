"""
Repository for TaskLog entity operations.
"""

from typing import List, Optional
from datetime import datetime
from db.models import TaskLog
from .base_repository import BaseRepository


class TaskLogRepository(BaseRepository[TaskLog]):
    """Repository for managing TaskLog entities."""

    def __init__(self):
        super().__init__(TaskLog)

    def create_tasklog(
        self,
        start_time: datetime,
        subject_id: int,
        end_time: Optional[datetime] = None,
        response: Optional[str] = None,
    ) -> TaskLog:
        """
        Create a new task log.

        Args:
            start_time: Start time of the task
            subject_id: The ID of the subject
            end_time: End time of the task (optional)
            response: Response from the task (optional)

        Returns:
            The created TaskLog instance
        """
        tasklog = TaskLog(
            start_time=start_time,
            end_time=end_time,
            response=response,
            subject_id=subject_id,
        )
        self.add(tasklog)
        return tasklog

    def get_tasklogs_by_subject(self, subject_id: int) -> List[TaskLog]:
        """
        Get all task logs for a specific subject.

        Args:
            subject_id: The ID of the subject

        Returns:
            List of task logs
        """
        return self.model.query.filter_by(subject_id=subject_id).all()

    def count_tasklogs_by_subject(self, subject_id: int) -> int:
        """
        Count task logs for a specific subject.

        Args:
            subject_id: The ID of the subject

        Returns:
            Number of task logs
        """
        return self.model.query.filter_by(subject_id=subject_id).count()
