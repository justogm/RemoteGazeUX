"""
Basic API integration tests.
These tests have been expanded in test_routes.py
"""

import json
from datetime import datetime


def test_get_subjects_empty(client):
    """Test getting subjects when database is empty."""
    resp = client.get("/api/get-subjects")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_subjects_after_create(client, app):
    """Test getting subjects after creating one."""
    with app.app_context():
        from repositories import SubjectRepository
        subject_repo = SubjectRepository()

        # Create a subject
        subj = subject_repo.create_subject(name="Juan", surname="Perez", age=30)
        subject_repo.commit()

    resp = client.get("/api/get-subjects")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    assert item.get("name") == "Juan"
    assert item.get("surname") == "Perez"
    assert item.get("age") == 30
