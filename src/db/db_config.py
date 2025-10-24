"""
Database configuration class.
"""

import os


class DatabaseConfig:
    """Configuration for database connection."""

    def __init__(self, basedir: str = None):
        """
        Initialize database configuration.

        Args:
            basedir: Base directory for the application
        """
        if basedir is None:
            basedir = os.path.abspath(os.path.dirname(__file__))

        self.basedir = basedir
        self.database_uri = None
        self.track_modifications = False

    def get_sqlite_uri(self, db_path: str = None) -> str:
        """
        Get SQLite database URI.

        Args:
            db_path: Path to the database file (relative or absolute)

        Returns:
            SQLite database URI
        """
        if db_path is None:
            db_path = os.path.join(self.basedir, "instance", "usergazetrack.db")

        # If it's a relative path, make it absolute
        if not os.path.isabs(db_path):
            db_path = os.path.join(self.basedir, db_path)

        return f"sqlite:///{db_path}"

    def configure_app(self, app, database_uri: str = None):
        """
        Configure Flask app with database settings.

        Args:
            app: Flask application instance
            database_uri: Database URI (if None, uses default SQLite)
        """
        if database_uri is None:
            database_uri = self.get_sqlite_uri()

        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = self.track_modifications

        self.database_uri = database_uri
