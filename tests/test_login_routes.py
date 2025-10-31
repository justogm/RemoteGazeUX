"""
Integration tests for login, logout, and protected routes.
"""

import pytest


@pytest.fixture
def test_user(app):
    """Create a test user for authentication tests."""
    from repositories import UserRepository

    with app.app_context():
        user_repo = UserRepository()
        user = user_repo.create_user(username="testuser", password="testpass123")
        user_repo.commit()
        return {"username": "testuser", "password": "testpass123", "id": user.id}


def test_login_page_loads(app, client):
    """Test that login page is accessible."""
    from flask_login import LoginManager

    with app.app_context():
        # Add a simple login route for testing
        @app.route("/login", methods=["GET", "POST"])
        def login():
            from flask import render_template, request, redirect, url_for
            from flask_login import login_user
            from repositories import UserRepository

            if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")

                user_repo = UserRepository()
                user = user_repo.get_user_by_username(username)

                if user and user.check_password(password):
                    login_user(user)
                    return redirect("/")

            return "Login form", 200

    response = client.get("/login")
    assert response.status_code == 200


def test_successful_login(app, client, test_user):
    """Test successful login flow."""
    from flask_login import current_user

    with app.app_context():
        # Add login route
        @app.route("/login", methods=["POST"])
        def login():
            from flask import request
            from flask_login import login_user
            from repositories import UserRepository

            username = request.form.get("username")
            password = request.form.get("password")

            user_repo = UserRepository()
            user = user_repo.get_user_by_username(username)

            if user and user.check_password(password):
                login_user(user)
                return "Success", 200

            return "Failed", 401

    # Attempt login
    response = client.post(
        "/login", data={"username": "testuser", "password": "testpass123"}
    )

    assert response.status_code == 200
    assert b"Success" in response.data


def test_failed_login_wrong_password(app, client, test_user):
    """Test login with wrong password."""
    with app.app_context():
        @app.route("/login", methods=["POST"])
        def login():
            from flask import request
            from flask_login import login_user
            from repositories import UserRepository

            username = request.form.get("username")
            password = request.form.get("password")

            user_repo = UserRepository()
            user = user_repo.get_user_by_username(username)

            if user and user.check_password(password):
                login_user(user)
                return "Success", 200

            return "Failed", 401

    response = client.post(
        "/login", data={"username": "testuser", "password": "wrongpassword"}
    )

    assert response.status_code == 401


def test_failed_login_nonexistent_user(app, client):
    """Test login with non-existent user."""
    with app.app_context():
        @app.route("/login", methods=["POST"])
        def login():
            from flask import request
            from repositories import UserRepository

            username = request.form.get("username")
            password = request.form.get("password")

            user_repo = UserRepository()
            user = user_repo.get_user_by_username(username)

            if user and user.check_password(password):
                return "Success", 200

            return "Failed", 401

    response = client.post(
        "/login", data={"username": "nonexistent", "password": "anypassword"}
    )

    assert response.status_code == 401


def test_logout_route(app, client, test_user):
    """Test logout functionality."""
    with app.app_context():
        @app.route("/login", methods=["POST"])
        def login():
            from flask import request
            from flask_login import login_user
            from repositories import UserRepository

            username = request.form.get("username")
            password = request.form.get("password")

            user_repo = UserRepository()
            user = user_repo.get_user_by_username(username)

            if user and user.check_password(password):
                login_user(user)
                return "Logged in", 200
            return "Failed", 401

        @app.route("/logout")
        def logout():
            from flask_login import logout_user

            logout_user()
            return "Logged out", 200

    # Login first
    client.post("/login", data={"username": "testuser", "password": "testpass123"})

    # Then logout
    response = client.get("/logout")
    assert response.status_code == 200
    assert b"Logged out" in response.data


def test_protected_route_without_login(app, client):
    """Test accessing protected route without being logged in."""
    from flask_login import login_required
    
    with app.app_context():
        @app.route("/login")
        def login():
            return "Login page", 200

        @app.route("/protected")
        @login_required
        def protected():
            return "Protected content", 200

    response = client.get("/protected")

    # Should redirect to login
    assert response.status_code == 302
    assert "/login" in response.location


def test_protected_route_with_login(app, client, test_user):
    """Test accessing protected route after logging in."""
    from flask_login import login_required
    
    with app.app_context():
        @app.route("/login", methods=["POST"])
        def login():
            from flask import request
            from flask_login import login_user
            from repositories import UserRepository

            username = request.form.get("username")
            password = request.form.get("password")

            user_repo = UserRepository()
            user = user_repo.get_user_by_username(username)

            if user and user.check_password(password):
                login_user(user)
                return "Logged in", 200
            return "Failed", 401

        @app.route("/protected")
        @login_required
        def protected():
            return "Protected content", 200

    # Login first
    client.post("/login", data={"username": "testuser", "password": "testpass123"})

    # Access protected route
    response = client.get("/protected")
    assert response.status_code == 200
    assert b"Protected content" in response.data


def test_session_persistence(app, client, test_user):
    """Test that session persists across requests."""
    from flask_login import login_required
    
    with app.app_context():
        @app.route("/login", methods=["POST"])
        def login():
            from flask import request
            from flask_login import login_user
            from repositories import UserRepository

            username = request.form.get("username")
            user_repo = UserRepository()
            user = user_repo.get_user_by_username(username)

            if user:
                login_user(user)
                return "Logged in", 200
            return "Failed", 401

        @app.route("/check")
        @login_required
        def check():
            from flask_login import current_user

            return f"User: {current_user.username}", 200

    # Login
    client.post("/login", data={"username": "testuser", "password": "testpass123"})

    # Multiple requests should maintain session
    response1 = client.get("/check")
    response2 = client.get("/check")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert b"testuser" in response1.data
    assert b"testuser" in response2.data


def test_current_user_access(app, client, test_user):
    """Test accessing current_user in protected routes."""
    from flask_login import login_required
    
    with app.app_context():
        @app.route("/login", methods=["POST"])
        def login():
            from flask import request
            from flask_login import login_user
            from repositories import UserRepository

            username = request.form.get("username")
            password = request.form.get("password")

            user_repo = UserRepository()
            user = user_repo.get_user_by_username(username)

            if user and user.check_password(password):
                login_user(user)
                return "Success", 200
            return "Failed", 401

        @app.route("/whoami")
        @login_required
        def whoami():
            from flask_login import current_user

            return f"Username: {current_user.username}, ID: {current_user.id}", 200

    # Login
    client.post("/login", data={"username": "testuser", "password": "testpass123"})

    # Check current user
    response = client.get("/whoami")
    assert response.status_code == 200
    assert b"Username: testuser" in response.data
    assert f"ID: {test_user['id']}".encode() in response.data
