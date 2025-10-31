"""
Tests for authentication system (User model, login, logout, protected routes).
"""

import pytest
from datetime import datetime


def test_user_model_creation(app):
    """Test creating a user with hashed password."""
    from db import User
    from repositories import UserRepository

    with app.app_context():
        user_repo = UserRepository()

        # Create a user
        user = user_repo.create_user(username="testuser", password="testpass123")
        user_repo.commit()

        # Verify user was created
        assert user.id is not None
        assert user.username == "testuser"
        assert user.password_hash is not None
        assert user.password_hash != "testpass123"  # Password should be hashed
        assert user.created_at is not None


def test_user_password_hashing(app):
    """Test that passwords are properly hashed and verified."""
    from db import User

    with app.app_context():
        user = User(username="hashtest", created_at=datetime.now())
        user.set_password("mypassword")

        # Password should be hashed
        assert user.password_hash != "mypassword"
        assert len(user.password_hash) > 20  # Hashed passwords are long

        # Correct password should verify
        assert user.check_password("mypassword") is True

        # Wrong password should not verify
        assert user.check_password("wrongpassword") is False


def test_user_repository_get_by_username(app):
    """Test retrieving a user by username."""
    from repositories import UserRepository

    with app.app_context():
        user_repo = UserRepository()

        # Create a user
        user = user_repo.create_user(username="john", password="pass123")
        user_repo.commit()

        # Retrieve by username
        found_user = user_repo.get_user_by_username("john")
        assert found_user is not None
        assert found_user.username == "john"

        # Non-existent user
        not_found = user_repo.get_user_by_username("nonexistent")
        assert not_found is None


def test_user_repository_user_exists(app):
    """Test checking if a user exists."""
    from repositories import UserRepository

    with app.app_context():
        user_repo = UserRepository()

        # User doesn't exist yet
        assert user_repo.user_exists("alice") is False

        # Create user
        user_repo.create_user(username="alice", password="pass123")
        user_repo.commit()

        # Now user exists
        assert user_repo.user_exists("alice") is True


def test_user_service_get_count(app):
    """Test getting user count via service."""
    from api.services import UserService
    from repositories import UserRepository

    with app.app_context():
        user_service = UserService()
        user_repo = UserRepository()

        # Initially no users
        assert user_service.get_user_count() == 0

        # Create users
        user_repo.create_user(username="user1", password="pass1")
        user_repo.create_user(username="user2", password="pass2")
        user_repo.commit()

        # Count should be 2
        assert user_service.get_user_count() == 2


def test_user_service_create_user_success(app):
    """Test creating a user via service."""
    from api.services import UserService

    with app.app_context():
        user_service = UserService()

        result = user_service.create_user(
            {"username": "newuser", "password": "password123"}
        )

        assert result["status"] == "success"
        assert result["user"]["username"] == "newuser"
        assert "id" in result["user"]


def test_user_service_create_user_missing_fields(app):
    """Test creating user with missing fields."""
    from api.services import UserService

    with app.app_context():
        user_service = UserService()

        # Missing password
        result = user_service.create_user({"username": "user1"})
        assert result["status"] == "error"
        assert "required" in result["message"].lower()

        # Missing username
        result = user_service.create_user({"password": "pass123"})
        assert result["status"] == "error"
        assert "required" in result["message"].lower()


def test_user_service_create_user_duplicate(app):
    """Test creating a user that already exists."""
    from api.services import UserService
    from repositories import UserRepository

    with app.app_context():
        user_service = UserService()
        user_repo = UserRepository()

        # Create first user
        user_repo.create_user(username="duplicate", password="pass123")
        user_repo.commit()

        # Try to create duplicate
        result = user_service.create_user(
            {"username": "duplicate", "password": "newpass"}
        )

        assert result["status"] == "error"
        assert "already exists" in result["message"].lower()


def test_user_service_create_user_short_password(app):
    """Test creating user with password too short."""
    from api.services import UserService

    with app.app_context():
        user_service = UserService()

        result = user_service.create_user({"username": "user1", "password": "123"})

        assert result["status"] == "error"
        assert "at least 4 characters" in result["message"].lower()


def test_api_user_count_endpoint(app, client):
    """Test GET /api/users/count endpoint."""
    from repositories import UserRepository

    with app.app_context():
        user_repo = UserRepository()

        # No users initially
        response = client.get("/api/users/count")
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 0

        # Create users
        user_repo.create_user(username="user1", password="pass1")
        user_repo.create_user(username="user2", password="pass2")
        user_repo.commit()

        # Check count
        response = client.get("/api/users/count")
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 2


def test_api_create_user_endpoint(app, client):
    """Test POST /api/users/create endpoint."""
    response = client.post(
        "/api/users/create",
        json={"username": "apiuser", "password": "apipass123"},
        content_type="application/json",
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert data["user"]["username"] == "apiuser"


def test_api_create_user_endpoint_invalid(app, client):
    """Test POST /api/users/create with invalid data."""
    # Missing password
    response = client.post(
        "/api/users/create",
        json={"username": "user1"},
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"


def test_flask_login_integration(app):
    """Test Flask-Login integration with User model."""
    from db import User
    from flask_login import UserMixin

    with app.app_context():
        user = User(username="logintest", created_at=datetime.now())

        # User should inherit from UserMixin
        assert isinstance(user, UserMixin)

        # UserMixin provides required methods
        assert hasattr(user, "is_authenticated")
        assert hasattr(user, "is_active")
        assert hasattr(user, "is_anonymous")
        assert hasattr(user, "get_id")


def test_login_route_renders(app, client):
    """Test that login route renders properly."""
    from flask_login import LoginManager

    # Configure Flask-Login for the test app
    with app.app_context():
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = "login"

        # Add login route
        @app.route("/login", methods=["GET", "POST"])
        def login():
            return "Login Page", 200

    response = client.get("/login")
    assert response.status_code == 200


def test_protected_route_requires_login(app, client):
    """Test that protected routes redirect to login."""
    from flask_login import login_required

    # Flask-Login ya está configurado en conftest.py
    with app.app_context():
        @app.route("/login")
        def login():
            return "Login Page", 200

        @app.route("/protected")
        @login_required
        def protected():
            return "Protected Content", 200

    # Without login, should redirect
    response = client.get("/protected")
    assert response.status_code == 302  # Redirect
    assert "/login" in response.location


def test_user_json_representation(app):
    """Test User.__json__() method."""
    from repositories import UserRepository

    with app.app_context():
        user_repo = UserRepository()
        user = user_repo.create_user(username="jsontest", password="pass123")
        user_repo.commit()

        json_data = user.__json__()

        assert json_data["id"] == user.id
        assert json_data["username"] == "jsontest"
        assert "password" not in json_data  # Password should not be exposed
        assert "password_hash" not in json_data
        assert "created_at" in json_data


def test_multiple_users_different_passwords(app):
    """Test that multiple users can have different passwords."""
    from repositories import UserRepository

    with app.app_context():
        user_repo = UserRepository()

        user1 = user_repo.create_user(username="user1", password="pass1")
        user2 = user_repo.create_user(username="user2", password="pass2")
        user_repo.commit()

        # Different password hashes
        assert user1.password_hash != user2.password_hash

        # Each user can verify their own password
        assert user1.check_password("pass1") is True
        assert user1.check_password("pass2") is False

        assert user2.check_password("pass2") is True
        assert user2.check_password("pass1") is False
