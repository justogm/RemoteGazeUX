import sys
import os
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Add the `src` directory itself so top-level imports inside `src` modules
# (for example `from db import ...`) resolve when importing `src.app`.
SRC_DIR = os.path.join(ROOT_DIR, "src")
if os.path.isdir(SRC_DIR) and SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import db the same way the source code does (from db, not from src.db)
# to ensure we're working with the same instance
from db import db, DatabaseManager


@pytest.fixture(scope="function")
def app():
    """Create a Flask app configured for testing with an in-memory SQLite DB."""
    from flask import Flask
    from src.api.routes import api_bp
    
    # Create a new Flask app instance for testing
    test_app = Flask(__name__, 
                     template_folder=os.path.join(SRC_DIR, "app/templates"),
                     static_folder=os.path.join(SRC_DIR, "app/static"))

    # Use in-memory sqlite for tests
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    # Initialize database with test app (using the global db instance)
    db.init_app(test_app)
    
    # Register blueprints
    test_app.register_blueprint(api_bp)
    
    # Initialize repositories with test context
    with test_app.app_context():
        db.create_all()
        
        # Import and configure repositories to use test db context
        from src.repositories import SubjectRepository, MeasurementRepository, StudyRepository
        test_app.subject_repository = SubjectRepository()
        test_app.measurement_repository = MeasurementRepository()
        test_app.study_repository = StudyRepository()

    yield test_app

    # Teardown: drop tables and remove app from db registry
    with test_app.app_context():
        db.drop_all()
        db.session.remove()
    
    # Clean up the db app registry to allow fresh initialization in next test
    if test_app in db._app_engines:
        del db._app_engines[test_app]


@pytest.fixture(scope="function")
def client(app):
    """Create a test client."""
    return app.test_client()
