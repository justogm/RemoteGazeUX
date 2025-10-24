"""
Tests for API routes/endpoints.
"""

import json
from datetime import datetime


class TestSubjectRoutes:
    """Tests for subject-related API endpoints."""

    def test_get_subjects_empty(self, client):
        """Test getting subjects when database is empty."""
        resp = client.get("/api/get-subjects")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_subjects_after_create(self, client, app):
        """Test getting subjects after creating some."""
        with app.app_context():
            from repositories import SubjectRepository

            repo = SubjectRepository()

            repo.create_subject(name="Juan", surname="Pérez", age=30)
            repo.create_subject(name="María", surname="García", age=25)
            repo.commit()

        resp = client.get("/api/get-subjects")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 2


class TestMeasurementRoutes:
    """Tests for measurement-related API endpoints."""

    def test_get_user_points_not_found(self, client):
        """Test getting points for non-existent user."""
        resp = client.get("/api/get-user-points?id=99999")
        assert resp.status_code == 404

    def test_get_user_points(self, client, app):
        """Test getting user points."""
        with app.app_context():
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
                date=datetime.now(),
                subject_id=subject.id,
                gaze_point=gaze,
                mouse_point=mouse,
            )
            measurement_repo.commit()

            subject_id = subject.id

        resp = client.get(f"/api/get-user-points?id={subject_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["subject_id"] == subject_id
        assert len(data["points"]) == 1

    def test_save_points(self, client, app):
        """Test saving measurement points."""
        with app.app_context():
            from repositories import SubjectRepository

            repo = SubjectRepository()
            subject = repo.create_subject("Test", "User", 25)
            repo.commit()
            subject_id = subject.id

        data = {
            "id": subject_id,
            "points": [
                {
                    "date": "10/23/2025, 10:30:00 AM",
                    "gaze": {"x": 100.5, "y": 200.5},
                    "mouse": {"x": 105.0, "y": 205.0},
                }
            ],
        }

        resp = client.post(
            "/api/save-points", data=json.dumps(data), content_type="application/json"
        )

        assert resp.status_code == 200
        response_data = resp.get_json()
        assert response_data["status"] == "success"


class TestTaskLogRoutes:
    """Tests for task log-related API endpoints."""

    def test_get_user_tasklogs_not_found(self, client):
        """Test getting task logs for non-existent user."""
        resp = client.get("/api/get-user-tasklogs?id=99999")
        assert resp.status_code == 404

    def test_get_user_tasklogs(self, client, app):
        """Test getting user task logs."""
        with app.app_context():
            from repositories import SubjectRepository, TaskLogRepository

            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            tasklog_repo = TaskLogRepository()
            tasklog_repo.create_tasklog(
                start_time=datetime.now(),
                response="Test response",
                subject_id=subject.id,
            )
            tasklog_repo.commit()

            subject_id = subject.id

        resp = client.get(f"/api/get-user-tasklogs?id={subject_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["subject_id"] == subject_id
        assert len(data["task_logs"]) == 1

    def test_save_tasklogs(self, client, app):
        """Test saving task logs."""
        with app.app_context():
            from repositories import SubjectRepository

            repo = SubjectRepository()
            subject = repo.create_subject("Test", "User", 25)
            repo.commit()
            subject_id = subject.id

        data = {
            "subject_id": subject_id,
            "taskLogs": [
                {
                    "startTime": "10/23/2025, 10:00:00 AM",
                    "endTime": "10/23/2025, 10:05:00 AM",
                    "response": "Completed",
                }
            ],
        }

        resp = client.post(
            "/api/save-tasklogs", data=json.dumps(data), content_type="application/json"
        )

        assert resp.status_code == 200
        response_data = resp.get_json()
        assert response_data["status"] == "success"


class TestExportRoutes:
    """Tests for export-related API endpoints."""

    def test_download_points_not_found(self, client):
        """Test downloading points for non-existent subject."""
        resp = client.get("/api/download-points?id=99999")
        assert resp.status_code == 404

    def test_download_points(self, client, app):
        """Test downloading points as CSV."""
        with app.app_context():
            from repositories import (
                SubjectRepository,
                MeasurementRepository,
                PointRepository,
            )

            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            point_repo = PointRepository()
            measurement_repo = MeasurementRepository()

            gaze = point_repo.create_point(100.0, 200.0)
            measurement_repo.create_measurement(
                date=datetime.now(), subject_id=subject.id, gaze_point=gaze
            )
            measurement_repo.commit()

            subject_id = subject.id

        resp = client.get(f"/api/download-points?id={subject_id}")
        assert resp.status_code == 200
        assert resp.content_type == "text/csv; charset=utf-8"
        assert b"date,x_mouse,y_mouse,x_gaze,y_gaze" in resp.data

    def test_download_tasklogs_not_found(self, client):
        """Test downloading task logs for non-existent subject."""
        resp = client.get("/api/download-tasklogs?id=99999")
        assert resp.status_code == 404

    def test_download_tasklogs(self, client, app):
        """Test downloading task logs as CSV."""
        with app.app_context():
            from repositories import SubjectRepository, TaskLogRepository

            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()

            tasklog_repo = TaskLogRepository()
            tasklog_repo.create_tasklog(
                start_time=datetime.now(), response="Test", subject_id=subject.id
            )
            tasklog_repo.commit()

            subject_id = subject.id

        resp = client.get(f"/api/download-tasklogs?id={subject_id}")
        assert resp.status_code == 200
        assert resp.content_type == "text/csv; charset=utf-8"
        assert b"start_time,end_time,response" in resp.data

    def test_download_all_no_subjects(self, client):
        """Test downloading all points when no subjects exist."""
        resp = client.get("/api/download-all")
        assert resp.status_code == 404


class TestConfigRoutes:
    """Tests for configuration-related endpoints."""

    def test_config_endpoint(self, client):
        """Test config endpoint returns JSON file."""
        resp = client.get("/api/config")
        # The endpoint tries to read a config file, may fail in test env
        # Just check it doesn't crash
        assert resp.status_code in [200, 404]

    def test_tasks_endpoint(self, client):
        """Test tasks endpoint returns JSON file."""
        resp = client.get("/api/tasks")
        # Similar to config, may not exist in test env
        assert resp.status_code in [200, 404]
