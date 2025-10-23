"""
Tests for database models.
"""

import pytest
from datetime import datetime
from db.models import Subject, Study, Measurement, Point, TaskLog


class TestSubjectModel:
    """Tests for Subject model."""
    
    def test_create_subject(self, app):
        """Test creating a subject."""
        with app.app_context():
            from db import db
            
            subject = Subject(name="Juan", surname="Pérez", age=25)
            db.session.add(subject)
            db.session.commit()
            
            assert subject.id is not None
            assert subject.name == "Juan"
            assert subject.surname == "Pérez"
            assert subject.age == 25
            assert subject.study_id is None
    
    def test_subject_with_study(self, app):
        """Test subject relationship with study."""
        with app.app_context():
            from db import db
            
            study = Study(
                name="Test Study",
                created_at=datetime.now()
            )
            db.session.add(study)
            db.session.commit()
            
            subject = Subject(
                name="María",
                surname="García",
                age=30,
                study_id=study.id
            )
            db.session.add(subject)
            db.session.commit()
            
            assert subject.study is not None
            assert subject.study.name == "Test Study"
            assert study.subjects[0].id == subject.id


class TestStudyModel:
    """Tests for Study model."""
    
    def test_create_study(self, app):
        """Test creating a study."""
        with app.app_context():
            from db import db
            
            study = Study(
                name="UX Study",
                description="Testing user experience",
                prototype_url="https://figma.com/test",
                prototype_image_path="/path/to/image.png",
                created_at=datetime.now()
            )
            db.session.add(study)
            db.session.commit()
            
            assert study.id is not None
            assert study.name == "UX Study"
            assert study.description == "Testing user experience"
            assert study.prototype_url == "https://figma.com/test"
            assert study.prototype_image_path == "/path/to/image.png"
            assert study.created_at is not None
    
    def test_study_json_serialization(self, app):
        """Test study JSON serialization."""
        with app.app_context():
            from db import db
            
            study = Study(
                name="Test",
                description="Desc",
                created_at=datetime(2025, 10, 23, 10, 0, 0)
            )
            db.session.add(study)
            db.session.commit()
            
            json_data = study.__json__()
            
            assert json_data["name"] == "Test"
            assert json_data["description"] == "Desc"
            assert "created_at" in json_data
    
    def test_study_str(self, app):
        """Test study string representation."""
        with app.app_context():
            from db import db
            
            study = Study(name="Test Study", created_at=datetime.now())
            db.session.add(study)
            db.session.commit()
            
            assert "Test Study" in str(study)
            assert str(study.id) in str(study)


class TestMeasurementModel:
    """Tests for Measurement model."""
    
    def test_create_measurement(self, app):
        """Test creating a measurement."""
        with app.app_context():
            from db import db
            
            subject = Subject(name="Test", surname="User", age=25)
            gaze_point = Point(x=100.0, y=200.0)
            mouse_point = Point(x=105.0, y=205.0)
            
            db.session.add_all([subject, gaze_point, mouse_point])
            db.session.commit()
            
            measurement = Measurement(
                date=datetime(2025, 10, 23, 10, 30, 0),
                subject_id=subject.id,
                gaze_point_id=gaze_point.id,
                mouse_point_id=mouse_point.id
            )
            db.session.add(measurement)
            db.session.commit()
            
            assert measurement.id is not None
            assert measurement.subject_id == subject.id
            assert measurement.gaze_point.x == 100.0
            assert measurement.gaze_point.y == 200.0
            assert measurement.mouse_point.x == 105.0
            assert measurement.mouse_point.y == 205.0
    
    def test_measurement_json_serialization(self, app):
        """Test measurement JSON serialization."""
        with app.app_context():
            from db import db
            
            subject = Subject(name="Test", surname="User", age=25)
            gaze_point = Point(x=100.0, y=200.0)
            
            db.session.add_all([subject, gaze_point])
            db.session.commit()
            
            measurement = Measurement(
                date=datetime(2025, 10, 23, 10, 30, 0),
                subject_id=subject.id,
                gaze_point_id=gaze_point.id
            )
            db.session.add(measurement)
            db.session.commit()
            
            json_data = measurement.__json__()
            
            assert "date" in json_data
            assert json_data["gaze_point"]["x"] == 100.0
            assert json_data["gaze_point"]["y"] == 200.0
    
    def test_measurement_str(self, app):
        """Test measurement string representation."""
        with app.app_context():
            from db import db
            
            subject = Subject(name="Test", surname="User", age=25)
            db.session.add(subject)
            db.session.commit()
            
            measurement = Measurement(
                date=datetime.now(),
                subject_id=subject.id
            )
            db.session.add(measurement)
            db.session.commit()
            
            str_repr = str(measurement)
            assert "Measurement" in str_repr


class TestPointModel:
    """Tests for Point model."""
    
    def test_create_point(self, app):
        """Test creating a point."""
        with app.app_context():
            from db import db
            
            point = Point(x=123.45, y=678.90)
            db.session.add(point)
            db.session.commit()
            
            assert point.id is not None
            assert point.x == 123.45
            assert point.y == 678.90
    
    def test_point_json_serialization(self, app):
        """Test point JSON serialization."""
        with app.app_context():
            from db import db
            
            point = Point(x=100.0, y=200.0)
            db.session.add(point)
            db.session.commit()
            
            json_data = point.__json__()
            
            assert json_data["x"] == 100.0
            assert json_data["y"] == 200.0
    
    def test_point_str(self, app):
        """Test point string representation."""
        with app.app_context():
            from db import db
            
            point = Point(x=50.5, y=75.5)
            db.session.add(point)
            db.session.commit()
            
            str_repr = str(point)
            assert "50.5" in str_repr
            assert "75.5" in str_repr


class TestTaskLogModel:
    """Tests for TaskLog model."""
    
    def test_create_tasklog(self, app):
        """Test creating a task log."""
        with app.app_context():
            from db import db
            
            subject = Subject(name="Test", surname="User", age=25)
            db.session.add(subject)
            db.session.commit()
            
            tasklog = TaskLog(
                start_time=datetime(2025, 10, 23, 10, 0, 0),
                end_time=datetime(2025, 10, 23, 10, 5, 0),
                response="Test response",
                subject_id=subject.id,
                task_description="Click button",
                task_type="navigation",
                task_version=1
            )
            db.session.add(tasklog)
            db.session.commit()
            
            assert tasklog.id is not None
            assert tasklog.start_time is not None
            assert tasklog.start_time == datetime(2025, 10, 23, 10, 0, 0)
            assert tasklog.end_time is not None
            assert tasklog.end_time == datetime(2025, 10, 23, 10, 5, 0)
            assert tasklog.response == "Test response"
            assert tasklog.subject_id == subject.id
            assert tasklog.task_description == "Click button"
            assert tasklog.task_type == "navigation"
            assert tasklog.task_version == 1

    def test_tasklog_json_serialization(self, app):
        """Test task log JSON serialization."""
        with app.app_context():
            from db import db
            
            subject = Subject(name="Test", surname="User", age=25)
            db.session.add(subject)
            db.session.commit()
            
            tasklog = TaskLog(
                start_time=datetime(2025, 10, 23, 10, 0, 0),
                end_time=datetime(2025, 10, 23, 10, 5, 0),
                response="Completed",
                subject_id=subject.id
            )
            db.session.add(tasklog)
            db.session.commit()
            
            json_data = tasklog.__json__()
            
            assert "start_time" in json_data
            assert "end_time" in json_data
            assert json_data["response"] == "Completed"
            assert json_data["subject_id"] == subject.id
    
    def test_tasklog_str(self, app):
        """Test task log string representation."""
        with app.app_context():
            from db import db
            
            subject = Subject(name="Test", surname="User", age=25)
            db.session.add(subject)
            db.session.commit()
            
            tasklog = TaskLog(
                start_time=datetime.now(),
                subject_id=subject.id
            )
            db.session.add(tasklog)
            db.session.commit()
            
            str_repr = str(tasklog)
            assert "TaskLog" in str_repr
            assert str(subject.id) in str_repr
    
    def test_tasklog_relationship(self, app):
        """Test task log relationship with subject."""
        with app.app_context():
            from db import db
            
            subject = Subject(name="Test", surname="User", age=25)
            db.session.add(subject)
            db.session.commit()
            
            tasklog = TaskLog(
                start_time=datetime.now(),
                subject_id=subject.id
            )
            db.session.add(tasklog)
            db.session.commit()
            
            assert tasklog.subject is not None
            assert tasklog.subject.name == "Test"
            assert tasklog.subject_id == subject.id
            assert tasklog.subject.surname == "User"
            assert len(subject.task_logs) == 1
            assert subject.task_logs[0].id == tasklog.id
