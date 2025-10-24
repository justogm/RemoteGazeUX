"""
Database manager for initialization and operations.
"""

from .models import db


class DatabaseManager:
    """Manager for database operations."""

    def __init__(self, app=None):
        """
        Initialize database manager.

        Args:
            app: Flask application instance (optional)
        """
        self.app = app
        self.db = db
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize database with Flask app.

        Args:
            app: Flask application instance
        """
        self.app = app
        self.db.init_app(app)

    def create_all(self):
        """Create all database tables."""
        if self.app is None:
            raise RuntimeError("Database manager not initialized with an app")

        with self.app.app_context():
            self.db.create_all()

    def drop_all(self):
        """Drop all database tables."""
        if self.app is None:
            raise RuntimeError("Database manager not initialized with an app")

        with self.app.app_context():
            self.db.drop_all()

    def reset_database(self):
        """Reset database by dropping and recreating all tables."""
        self.drop_all()
        self.create_all()

    def get_session(self):
        """
        Get database session.

        Returns:
            SQLAlchemy session
        """
        return self.db.session
