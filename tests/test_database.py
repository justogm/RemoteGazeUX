"""
Tests for database manager and configuration.
"""

import pytest
import os
from flask import Flask
from db import DatabaseManager, DatabaseConfig, db


class TestDatabaseManager:
    """Tests for DatabaseManager class."""
    
    def test_create_database_manager(self):
        """Test creating a database manager without app."""
        manager = DatabaseManager()
        assert manager.app is None
        assert manager.db is not None
    
    def test_create_all_with_fresh_app(self):
        """Test creating all tables with a fresh app."""
        # Create a fresh Flask app for this test
        fresh_app = Flask(__name__)
        fresh_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        fresh_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        with fresh_app.app_context():
            # Create new manager and initialize
            fresh_db = DatabaseManager()
            fresh_db.db.init_app(fresh_app)
            fresh_db.app = fresh_app
            
            # Create tables
            fresh_db.create_all()
            
            # Verify doesn't crash
            assert True
    
    def test_get_session(self, app):
        """Test getting database session."""
        with app.app_context():
            # Use the existing db from the app fixture
            from db import db
            manager = DatabaseManager()
            manager.app = app
            manager.db = db
            
            session = manager.get_session()
            assert session is not None
    
    def test_manager_without_app_error(self):
        """Test that operations fail without app."""
        manager = DatabaseManager()
        
        with pytest.raises(RuntimeError, match="not initialized with an app"):
            manager.create_all()
        
        with pytest.raises(RuntimeError, match="not initialized with an app"):
            manager.drop_all()
        
        with pytest.raises(RuntimeError, match="not initialized with an app"):
            manager.reset_database()


class TestDatabaseConfig:
    """Tests for DatabaseConfig class."""
    
    def test_create_database_config(self):
        """Test creating database config."""
        config = DatabaseConfig("/test/path")
        assert config.basedir == "/test/path"
    
    def test_configure_app(self):
        """Test configuring Flask app."""
        basedir = os.path.abspath(os.path.dirname(__file__))
        config = DatabaseConfig(basedir)
        
        # Create a fresh app for this test
        fresh_app = Flask(__name__)
        config.configure_app(fresh_app)
        
        assert 'SQLALCHEMY_DATABASE_URI' in fresh_app.config
        assert 'SQLALCHEMY_TRACK_MODIFICATIONS' in fresh_app.config
        assert fresh_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    
    def test_database_uri_format(self):
        """Test that database URI is correctly formatted."""
        basedir = os.path.abspath(os.path.dirname(__file__))
        config = DatabaseConfig(basedir)
        
        fresh_app = Flask(__name__)
        config.configure_app(fresh_app)
        
        uri = fresh_app.config['SQLALCHEMY_DATABASE_URI']
        assert uri.startswith('sqlite:///')
        
        assert 'usergazetrack.db' in uri or 'database.db' in uri
