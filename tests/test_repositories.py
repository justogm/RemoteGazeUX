"""
Tests for all repository classes.
"""

import pytest
from datetime import datetime
from db.models import Subject, Study, Measurement, Point, TaskLog


class TestSubjectRepository:
    """Tests for SubjectRepository."""
    
    def test_create_subject(self, app):
        """Test creating a subject."""
        with app.app_context():
            from repositories import SubjectRepository
            repo = SubjectRepository()
            
            subject = repo.create_subject(
                name="Juan",
                surname="Pérez",
                age=25
            )
            repo.commit()
            
            assert subject.id is not None
            assert subject.name == "Juan"
            assert subject.surname == "Pérez"
            assert subject.age == 25
            assert subject.study_id is None
    
    def test_create_subject_with_study(self, app):
        """Test creating a subject associated with a study."""
        with app.app_context():
            from repositories import SubjectRepository, StudyRepository
            
            study_repo = StudyRepository()
            study = study_repo.create_study(name="Test Study")
            
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject(
                name="María",
                surname="González",
                age=30,
                study_id=study.id
            )
            subject_repo.commit()
            
            assert subject.study_id == study.id
            assert subject.study is not None
            assert subject.study.name == "Test Study"
    
    def test_get_all_subjects(self, app):
        """Test retrieving all subjects."""
        with app.app_context():
            from repositories import SubjectRepository
            repo = SubjectRepository()
            
            # Initially empty
            assert len(repo.get_all_subjects()) == 0
            
            # Add subjects
            repo.create_subject("Ana", "López", 22)
            repo.create_subject("Pedro", "Martínez", 28)
            repo.commit()
            
            subjects = repo.get_all_subjects()
            assert len(subjects) == 2
    
    def test_get_subject_by_id(self, app):
        """Test getting a subject by ID."""
        with app.app_context():
            from repositories import SubjectRepository
            repo = SubjectRepository()
            
            subject = repo.create_subject("Carlos", "Rodríguez", 35)
            repo.commit()
            
            retrieved = repo.get_subject_by_id(subject.id)
            assert retrieved is not None
            assert retrieved.id == subject.id
            assert retrieved.name == "Carlos"
            
            # Non-existent ID
            assert repo.get_subject_by_id(99999) is None


class TestStudyRepository:
    """Tests for StudyRepository."""
    
    def test_create_study(self, app):
        """Test creating a study."""
        with app.app_context():
            from repositories import StudyRepository
            repo = StudyRepository()
            
            study = repo.create_study(
                name="User Experience Study",
                description="Testing user interactions",
                prototype_url="https://figma.com/test",
                prototype_image_path="/path/to/image.png"
            )
            
            assert study.id is not None
            assert study.name == "User Experience Study"
            assert study.description == "Testing user interactions"
            assert study.prototype_url == "https://figma.com/test"
            assert study.prototype_image_path == "/path/to/image.png"
            assert study.created_at is not None
    
    def test_get_all_studies(self, app):
        """Test retrieving all studies ordered by date."""
        with app.app_context():
            from repositories import StudyRepository
            repo = StudyRepository()
            
            study1 = repo.create_study(name="Study 1")
            study2 = repo.create_study(name="Study 2")
            study3 = repo.create_study(name="Study 3")
            
            studies = repo.get_all_studies()
            assert len(studies) == 3
            # Should be ordered newest first
            assert studies[0].id == study3.id
            assert studies[1].id == study2.id
            assert studies[2].id == study1.id
    
    def test_get_study_by_id(self, app):
        """Test getting a study by ID."""
        with app.app_context():
            from repositories import StudyRepository
            repo = StudyRepository()
            
            study = repo.create_study(name="Test Study")
            
            retrieved = repo.get_study_by_id(study.id)
            assert retrieved is not None
            assert retrieved.id == study.id
            assert retrieved.name == "Test Study"
    
    def test_get_study_by_name(self, app):
        """Test getting a study by name."""
        with app.app_context():
            from repositories import StudyRepository
            repo = StudyRepository()
            
            study = repo.create_study(name="Unique Study Name")
            
            retrieved = repo.get_study_by_name("Unique Study Name")
            assert retrieved is not None
            assert retrieved.id == study.id
            
            # Non-existent name
            assert repo.get_study_by_name("Non-existent") is None
    
    def test_update_study(self, app):
        """Test updating a study."""
        with app.app_context():
            from repositories import StudyRepository
            repo = StudyRepository()
            
            study = repo.create_study(
                name="Original Name",
                description="Original Description"
            )
            
            updated = repo.update_study(
                study.id,
                name="Updated Name",
                description="Updated Description",
                prototype_url="https://new-url.com"
            )
            
            assert updated is not None
            assert updated.name == "Updated Name"
            assert updated.description == "Updated Description"
            assert updated.prototype_url == "https://new-url.com"
    
    def test_delete_study(self, app):
        """Test deleting a study."""
        with app.app_context():
            from repositories import StudyRepository
            repo = StudyRepository()
            
            study = repo.create_study(name="To Delete")
            study_id = study.id
            
            assert repo.delete_study(study_id) is True
            assert repo.get_study_by_id(study_id) is None
            
            # Deleting non-existent study
            assert repo.delete_study(99999) is False
    
    def test_get_active_study(self, app):
        """Test getting the most recent study."""
        with app.app_context():
            from repositories import StudyRepository
            repo = StudyRepository()
            
            # No studies
            assert repo.get_active_study() is None
            
            study1 = repo.create_study(name="Old Study")
            study2 = repo.create_study(name="Recent Study")
            
            active = repo.get_active_study()
            assert active is not None
            assert active.id == study2.id


class TestMeasurementRepository:
    """Tests for MeasurementRepository."""
    
    def test_create_measurement(self, app):
        """Test creating a measurement."""
        with app.app_context():
            from repositories import (
                MeasurementRepository, 
                SubjectRepository, 
                PointRepository
            )
            
            # Create subject and points
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()
            
            point_repo = PointRepository()
            gaze = point_repo.create_point(100.5, 200.5)
            mouse = point_repo.create_point(105.0, 205.0)
            point_repo.commit()
            
            # Create measurement
            measurement_repo = MeasurementRepository()
            measurement = measurement_repo.create_measurement(
                date=datetime(2025, 10, 23, 10, 30, 0),
                subject_id=subject.id,
                gaze_point=gaze,
                mouse_point=mouse
            )
            measurement_repo.commit()
            
            assert measurement.id is not None
            assert measurement.subject_id == subject.id
            assert measurement.gaze_point_id == gaze.id
            assert measurement.mouse_point_id == mouse.id
    
    def test_get_measurements_by_subject(self, app):
        """Test retrieving measurements for a subject."""
        with app.app_context():
            from repositories import (
                MeasurementRepository,
                SubjectRepository,
                PointRepository
            )
            
            subject_repo = SubjectRepository()
            subject1 = subject_repo.create_subject("User1", "Test", 25)
            subject2 = subject_repo.create_subject("User2", "Test", 30)
            subject_repo.commit()
            
            point_repo = PointRepository()
            measurement_repo = MeasurementRepository()
            
            # Create measurements for subject1
            for i in range(3):
                point = point_repo.create_point(i * 10.0, i * 20.0)
                measurement_repo.create_measurement(
                    date=datetime.now(),
                    subject_id=subject1.id,
                    gaze_point=point
                )
            
            # Create measurement for subject2
            point = point_repo.create_point(100.0, 200.0)
            measurement_repo.create_measurement(
                date=datetime.now(),
                subject_id=subject2.id,
                gaze_point=point
            )
            measurement_repo.commit()
            
            measurements1 = measurement_repo.get_measurements_by_subject(subject1.id)
            measurements2 = measurement_repo.get_measurements_by_subject(subject2.id)
            
            assert len(measurements1) == 3
            assert len(measurements2) == 1


class TestPointRepository:
    """Tests for PointRepository."""
    
    def test_create_point(self, app):
        """Test creating a point."""
        with app.app_context():
            from repositories import PointRepository
            repo = PointRepository()
            
            point = repo.create_point(x=123.45, y=678.90)
            repo.commit()
            
            assert point.id is not None
            assert point.x == 123.45
            assert point.y == 678.90
    
    def test_create_multiple_points(self, app):
        """Test creating multiple points."""
        with app.app_context():
            from repositories import PointRepository
            repo = PointRepository()
            
            points_data = [(10.0, 20.0), (30.0, 40.0), (50.0, 60.0)]
            points = []
            
            for x, y in points_data:
                point = repo.create_point(x, y)
                points.append(point)
            
            repo.commit()
            
            assert len(points) == 3
            assert all(p.id is not None for p in points)


class TestTaskLogRepository:
    """Tests for TaskLogRepository."""
    
    def test_create_tasklog(self, app):
        """Test creating a task log."""
        with app.app_context():
            from repositories import TaskLogRepository, SubjectRepository
            
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()
            
            tasklog_repo = TaskLogRepository()
            start = datetime(2025, 10, 23, 10, 0, 0)
            end = datetime(2025, 10, 23, 10, 5, 0)
            
            tasklog = tasklog_repo.create_tasklog(
                start_time=start,
                end_time=end,
                response="Test response",
                subject_id=subject.id
            )
            tasklog_repo.commit()
            
            assert tasklog.id is not None
            assert tasklog.start_time == start
            assert tasklog.end_time == end
            assert tasklog.response == "Test response"
            assert tasklog.subject_id == subject.id
    
    def test_get_tasklogs_by_subject(self, app):
        """Test retrieving task logs for a subject."""
        with app.app_context():
            from repositories import TaskLogRepository, SubjectRepository
            
            subject_repo = SubjectRepository()
            subject1 = subject_repo.create_subject("User1", "Test", 25)
            subject2 = subject_repo.create_subject("User2", "Test", 30)
            subject_repo.commit()
            
            tasklog_repo = TaskLogRepository()
            
            # Create task logs for subject1
            for i in range(3):
                tasklog_repo.create_tasklog(
                    start_time=datetime.now(),
                    subject_id=subject1.id,
                    response=f"Response {i}"
                )
            
            # Create task log for subject2
            tasklog_repo.create_tasklog(
                start_time=datetime.now(),
                subject_id=subject2.id,
                response="Response"
            )
            tasklog_repo.commit()
            
            logs1 = tasklog_repo.get_tasklogs_by_subject(subject1.id)
            logs2 = tasklog_repo.get_tasklogs_by_subject(subject2.id)
            
            assert len(logs1) == 3
            assert len(logs2) == 1
    
    def test_count_tasklogs_by_subject(self, app):
        """Test counting task logs for a subject."""
        with app.app_context():
            from repositories import TaskLogRepository, SubjectRepository
            
            subject_repo = SubjectRepository()
            subject = subject_repo.create_subject("Test", "User", 25)
            subject_repo.commit()
            
            tasklog_repo = TaskLogRepository()
            
            assert tasklog_repo.count_tasklogs_by_subject(subject.id) == 0
            
            for i in range(5):
                tasklog_repo.create_tasklog(
                    start_time=datetime.now(),
                    subject_id=subject.id
                )
            tasklog_repo.commit()
            
            assert tasklog_repo.count_tasklogs_by_subject(subject.id) == 5


class TestBaseRepository:
    """Tests for BaseRepository common functionality."""
    
    def test_add_and_commit(self, app):
        """Test add and commit operations."""
        with app.app_context():
            from repositories import SubjectRepository
            repo = SubjectRepository()
            
            subject = Subject(name="Test", surname="User", age=25)
            repo.add(subject)
            repo.commit()
            
            assert subject.id is not None
    
    def test_delete(self, app):
        """Test delete operation."""
        with app.app_context():
            from repositories import SubjectRepository
            repo = SubjectRepository()
            
            subject = repo.create_subject("To Delete", "User", 25)
            repo.commit()
            subject_id = subject.id
            
            repo.delete(subject)
            repo.commit()
            
            assert repo.get_by_id(subject_id) is None
    
    def test_rollback(self, app):
        """Test rollback operation."""
        with app.app_context():
            from repositories import SubjectRepository
            repo = SubjectRepository()
            
            subject = repo.create_subject("Test", "User", 25)
            repo.commit()
            
            # Modify and rollback
            subject.name = "Modified"
            repo.rollback()
            
            # Should still be original
            retrieved = repo.get_by_id(subject.id)
            assert retrieved.name == "Test"
