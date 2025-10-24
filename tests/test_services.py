"""
Tests for API services.
"""

import pytest
import io
from datetime import datetime
from db.models import Subject, Point, Measurement, TaskLog


class TestSubjectService:
    """Tests for SubjectService."""

    def test_get_all_subjects_empty(self, app):
        """Test getting all subjects when DB is empty."""
        with app.app_context():
            from api.services import SubjectService

            service = SubjectService()

            subjects = service.get_all_subjects()
            assert isinstance(subjects, list)
            assert len(subjects) == 0

    def test_get_all_subjects(self, app):
        """Test getting all subjects."""
        with app.app_context():
            from api.services import SubjectService
            from repositories import SubjectRepository

            # Create test subjects
            repo = SubjectRepository()
            repo.create_subject("Juan", "Pérez", 25)
            repo.create_subject("María", "García", 30)
            repo.commit()

            service = SubjectService()
            subjects = service.get_all_subjects()

            assert len(subjects) == 2
            assert subjects[0]["name"] == "Juan"
            assert subjects[0]["surname"] == "Pérez"
            assert subjects[0]["age"] == 25
            assert subjects[1]["name"] == "María"

    def test_get_subject_by_id(self, app):
        """Test getting a subject by ID."""
        with app.app_context():
            from api.services import SubjectService
            from repositories import SubjectRepository

            repo = SubjectRepository()
            subject = repo.create_subject("Test", "User", 25)
            repo.commit()

            service = SubjectService()
            retrieved = service.get_subject_by_id(subject.id)

            assert retrieved is not None
            assert retrieved.name == "Test"
            assert retrieved.surname == "User"

            # Non-existent
            assert service.get_subject_by_id(99999) is None


class TestMeasurementService:
    """Tests for MeasurementService."""

    def test_save_points(self, app):
        """Test saving measurement points."""
        with app.app_context():
            from api.services import MeasurementService
            from repositories import SubjectRepository

            # Create subject
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            # Prepare data
            data = {
                "id": subject.id,
                "points": [
                    {
                        "date": "10/23/2025, 10:30:00 AM",
                        "gaze": {"x": 100.5, "y": 200.5},
                        "mouse": {"x": 105.0, "y": 205.0},
                    },
                    {
                        "date": "10/23/2025, 10:30:01 AM",
                        "gaze": {"x": 110.0, "y": 210.0},
                        "mouse": {"x": 115.0, "y": 215.0},
                    },
                ],
            }

            service = MeasurementService()
            result = service.save_points(data)

            assert result["status"] == "success"

            # Verify measurements were saved
            from repositories import MeasurementRepository

            measurement_repo = MeasurementRepository()
            measurements = measurement_repo.get_measurements_by_subject(subject.id)

            assert len(measurements) == 2
            assert measurements[0].gaze_point.x == 100.5
            assert measurements[0].mouse_point.y == 205.0

    def test_get_user_points(self, app):
        """Test getting measurement points for a user."""
        with app.app_context():
            from api.services import MeasurementService
            from repositories import (
                SubjectRepository,
                MeasurementRepository,
                PointRepository,
            )

            # Create subject and measurements
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            point_repo = PointRepository()
            measurement_repo = MeasurementRepository()

            gaze = point_repo.create_point(100.0, 200.0)
            mouse = point_repo.create_point(105.0, 205.0)
            measurement_repo.create_measurement(
                date=datetime(2025, 10, 23, 10, 30, 0),
                subject_id=subject.id,
                gaze_point=gaze,
                mouse_point=mouse,
            )
            measurement_repo.commit()

            service = MeasurementService()
            result = service.get_user_points(subject.id)

            assert result is not None
            assert result["subject_id"] == subject.id
            assert len(result["points"]) == 1
            assert result["points"][0]["x_gaze"] == 100.0
            assert result["points"][0]["y_mouse"] == 205.0

    def test_get_user_points_not_found(self, app):
        """Test getting points for non-existent user."""
        with app.app_context():
            from api.services import MeasurementService

            service = MeasurementService()
            result = service.get_user_points(99999)

            assert result is None


class TestTaskLogService:
    """Tests for TaskLogService."""

    def test_save_tasklogs(self, app):
        """Test saving task logs."""
        with app.app_context():
            from api.services import TaskLogService
            from repositories import SubjectRepository

            # Create subject
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            # Prepare data
            data = {
                "subject_id": subject.id,
                "taskLogs": [
                    {
                        "startTime": "10/23/2025, 10:00:00 AM",
                        "endTime": "10/23/2025, 10:05:00 AM",
                        "response": "Completed",
                    },
                    {
                        "startTime": "10/23/2025, 10:10:00 AM",
                        "endTime": None,
                        "response": "In progress",
                    },
                ],
            }

            service = TaskLogService()
            result = service.save_tasklogs(data)

            assert result["status"] == "success"
            assert "message" in result

            # Verify logs were saved
            from repositories import TaskLogRepository

            tasklog_repo = TaskLogRepository()
            logs = tasklog_repo.get_tasklogs_by_subject(subject.id)

            assert len(logs) == 2
            assert logs[0].response == "Completed"
            assert logs[1].end_time is None

    def test_get_user_tasklogs(self, app):
        """Test getting task logs for a user."""
        with app.app_context():
            from api.services import TaskLogService
            from repositories import SubjectRepository, TaskLogRepository

            # Create subject and task logs
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            tasklog_repo = TaskLogRepository()
            tasklog_repo.create_tasklog(
                start_time=datetime(2025, 10, 23, 10, 0, 0),
                end_time=datetime(2025, 10, 23, 10, 5, 0),
                response="Test response",
                subject_id=subject.id,
            )
            tasklog_repo.commit()

            service = TaskLogService()
            result = service.get_user_tasklogs(subject.id)

            assert result is not None
            assert result["subject_id"] == subject.id
            assert len(result["task_logs"]) == 1
            assert result["task_logs"][0]["response"] == "Test response"

    def test_get_user_tasklogs_not_found(self, app):
        """Test getting task logs for non-existent user."""
        with app.app_context():
            from api.services import TaskLogService

            service = TaskLogService()
            result = service.get_user_tasklogs(99999)

            assert result is None


class TestExportService:
    """Tests for ExportService."""

    def test_export_points_csv(self, app):
        """Test exporting points to CSV."""
        with app.app_context():
            from api.services import ExportService
            from repositories import (
                SubjectRepository,
                MeasurementRepository,
                PointRepository,
            )

            # Create subject and measurements
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            point_repo = PointRepository()
            measurement_repo = MeasurementRepository()

            gaze = point_repo.create_point(100.0, 200.0)
            mouse = point_repo.create_point(105.0, 205.0)
            measurement_repo.create_measurement(
                date=datetime(2025, 10, 23, 10, 30, 0),
                subject_id=subject.id,
                gaze_point=gaze,
                mouse_point=mouse,
            )
            measurement_repo.commit()

            service = ExportService()
            csv_data = service.export_points_csv(subject.id)

            assert csv_data is not None
            assert isinstance(csv_data, io.BytesIO)

            # Read CSV content
            csv_content = csv_data.read().decode("utf-8")
            assert "date,x_mouse,y_mouse,x_gaze,y_gaze" in csv_content
            assert "100.0" in csv_content
            assert "200.0" in csv_content

    def test_export_points_csv_not_found(self, app):
        """Test exporting points for non-existent subject."""
        with app.app_context():
            from api.services import ExportService

            service = ExportService()
            csv_data = service.export_points_csv(99999)

            assert csv_data is None

    def test_export_tasklogs_csv(self, app):
        """Test exporting task logs to CSV."""
        with app.app_context():
            from api.services import ExportService
            from repositories import SubjectRepository, TaskLogRepository

            # Create subject and task log
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            tasklog_repo = TaskLogRepository()
            tasklog_repo.create_tasklog(
                start_time=datetime(2025, 10, 23, 10, 0, 0),
                end_time=datetime(2025, 10, 23, 10, 5, 0),
                response="Test",
                subject_id=subject.id,
            )
            tasklog_repo.commit()

            service = ExportService()
            csv_data = service.export_tasklogs_csv(subject.id)

            assert csv_data is not None
            assert isinstance(csv_data, io.BytesIO)

            csv_content = csv_data.read().decode("utf-8")
            assert "start_time,end_time,response" in csv_content
            assert "Test" in csv_content

    def test_export_tasklogs_csv_not_found(self, app):
        """Test exporting task logs for non-existent subject."""
        with app.app_context():
            from api.services import ExportService

            service = ExportService()
            csv_data = service.export_tasklogs_csv(99999)

            assert csv_data is None

    def test_export_all_points_csv_empty(self, app):
        """Test exporting all points when no subjects exist."""
        with app.app_context():
            from api.services import ExportService

            service = ExportService()
            csv_data = service.export_all_points_csv()

            assert csv_data is None
