"""
API services for the user gaze tracking application.
Contains business logic for data processing and database operations.
"""

import csv
import io
from datetime import datetime
import numpy as np
from db import db, Subject, Point, Measurement, TaskLog
from repositories import (
    SubjectRepository,
    MeasurementRepository,
    PointRepository,
    TaskLogRepository,
)


class SubjectService:
    """Service class for managing subjects."""

    def __init__(self):
        self.repository = SubjectRepository()

    def get_all_subjects(self):
        """Get all subjects with their basic information."""
        subjects = self.repository.get_all_subjects()
        return [
            {
                "id": subject.id,
                "name": subject.name,
                "surname": subject.surname,
                "age": subject.age,
            }
            for subject in subjects
        ]

    def get_subject_by_id(self, subject_id):
        """Get a subject by its ID."""
        return self.repository.get_subject_by_id(subject_id)


class MeasurementService:
    """Service class for managing measurements."""

    def __init__(self):
        self.repository = MeasurementRepository()
        self.point_repository = PointRepository()

    def save_points(self, data):
        """Save measurement points to the database."""
        points = data["points"]
        subject_id = data["id"]

        for point in points:
            date = datetime.strptime(point["date"], "%m/%d/%Y, %I:%M:%S %p")

            gaze_point = self.point_repository.create_point(
                x=point["gaze"]["x"],
                y=point["gaze"]["y"],
            )

            mouse_point = self.point_repository.create_point(
                x=point["mouse"]["x"],
                y=point["mouse"]["y"],
            )

            self.repository.create_measurement(
                date=date,
                subject_id=subject_id,
                gaze_point=gaze_point,
                mouse_point=mouse_point,
            )

        self.repository.commit()
        return {"status": "success"}

    def get_user_points(self, subject_id):
        """Get measurement points for a specific subject."""
        subject_service = SubjectService()
        subject = subject_service.get_subject_by_id(subject_id)

        if not subject:
            return None

        measurements = self.repository.get_measurements_by_subject(subject.id)

        points = []
        for measurement in measurements:
            point = {
                "date": measurement.date.strftime("%Y-%m-%d %H:%M:%S"),
                "x_mouse": (
                    measurement.mouse_point.x if measurement.mouse_point else None
                ),
                "y_mouse": (
                    measurement.mouse_point.y if measurement.mouse_point else None
                ),
                "x_gaze": measurement.gaze_point.x if measurement.gaze_point else None,
                "y_gaze": measurement.gaze_point.y if measurement.gaze_point else None,
            }
            points.append(point)

        return {"subject_id": subject_id, "points": points}


class TaskLogService:
    """Service class for managing task logs."""

    def __init__(self):
        self.repository = TaskLogRepository()

    def save_tasklogs(self, data):
        """Save task logs to the database."""
        task_logs = data["taskLogs"]
        subject_id = data["subject_id"]

        for log in task_logs:
            self.repository.create_tasklog(
                start_time=datetime.strptime(log["startTime"], "%m/%d/%Y, %I:%M:%S %p"),
                end_time=(
                    datetime.strptime(log["endTime"], "%m/%d/%Y, %I:%M:%S %p")
                    if log["endTime"]
                    else None
                ),
                response=log["response"],
                subject_id=subject_id,
            )

        self.repository.commit()
        return {"status": "success", "message": "TaskLogs saved successfully."}

    def get_user_tasklogs(self, subject_id):
        """Get task logs for a specific subject."""
        subject_service = SubjectService()
        subject = subject_service.get_subject_by_id(subject_id)

        if not subject:
            return None

        task_logs = self.repository.get_tasklogs_by_subject(subject.id)
        task_logs_info = [
            {
                "start_time": log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": (
                    log.end_time.strftime("%Y-%m-%d %H:%M:%S") if log.end_time else None
                ),
                "response": log.response,
            }
            for log in task_logs
        ]
        return {"subject_id": subject_id, "task_logs": task_logs_info}


class ExportService:
    """Service class for data export functionality."""

    def __init__(self):
        self.subject_repository = SubjectRepository()
        self.measurement_repository = MeasurementRepository()
        self.tasklog_repository = TaskLogRepository()

    def export_points_csv(self, subject_id):
        """Export measurement points for a subject as CSV."""
        subject = self.subject_repository.get_subject_by_id(subject_id)

        if not subject:
            return None

        measurements = self.measurement_repository.get_measurements_by_subject(
            subject.id
        )

        si = io.StringIO()
        csv_writer = csv.writer(si)

        csv_writer.writerow(["date", "x_mouse", "y_mouse", "x_gaze", "y_gaze"])

        for measurement in measurements:
            row = [
                measurement.date.strftime("%Y-%m-%d %H:%M:%S"),
                measurement.mouse_point.x if measurement.mouse_point else None,
                measurement.mouse_point.y if measurement.mouse_point else None,
                measurement.gaze_point.x if measurement.gaze_point else None,
                measurement.gaze_point.y if measurement.gaze_point else None,
            ]
            csv_writer.writerow(row)

        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))

    def export_tasklogs_csv(self, subject_id):
        """Export task logs for a subject as CSV."""
        subject = self.subject_repository.get_subject_by_id(subject_id)

        if not subject:
            return None

        si = io.StringIO()
        csv_writer = csv.writer(si)

        csv_writer.writerow(["start_time", "end_time", "response"])

        task_logs = self.tasklog_repository.get_tasklogs_by_subject(subject_id)

        for log in task_logs:
            row = [
                log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                log.end_time.strftime("%Y-%m-%d %H:%M:%S") if log.end_time else None,
                log.response,
            ]
            csv_writer.writerow(row)

        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))

    def export_all_points_csv(self):
        """Export measurement points for all subjects as CSV."""
        all_subjects = self.subject_repository.get_all_subjects()

        if len(all_subjects) == 0:
            return None

        si = io.StringIO()
        csv_writer = csv.DictWriter(si, fieldnames=["id", "x", "y"])
        csv_writer.writeheader()

        for subject in all_subjects:
            points = Point.query.filter_by(subject_id=subject.id).all()
            points_dict = [point.__json__() for point in points]

            subject_id = int(subject.id)

            points_np = np.array([[subject_id, p["x"], p["y"]] for p in points_dict])

            for point in points_np:
                csv_writer.writerow({"id": point[0], "x": point[1], "y": point[2]})

        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))
