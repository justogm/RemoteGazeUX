"""
Configuration manager for loading and managing application configuration.
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration from JSON files."""

    def __init__(self, config_dir: str = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            basedir = os.path.abspath(os.path.dirname(__file__))
            config_dir = os.path.join(basedir, "..", "config")

        self.config_dir = os.path.abspath(config_dir)
        self._config: Dict[str, Any] = {}
        self._tasks: Dict[str, Any] = {}

    def load_config(self, filename: str = "config.json") -> Dict[str, Any]:
        """
        Load configuration from JSON file.

        Args:
            filename: Name of the configuration file

        Returns:
            Dictionary containing configuration data
        """
        config_path = os.path.join(self.config_dir, filename)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = json.load(f)

        return self._config

    def load_tasks(self, filename: str = "tasks.json") -> Dict[str, Any]:
        """
        Load tasks configuration from JSON file.

        Args:
            filename: Name of the tasks file

        Returns:
            Dictionary containing tasks data
        """
        tasks_path = os.path.join(self.config_dir, filename)

        if not os.path.exists(tasks_path):
            raise FileNotFoundError(f"Tasks file not found: {tasks_path}")

        with open(tasks_path, "r", encoding="utf-8") as f:
            self._tasks = json.load(f)

        return self._tasks

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key: The configuration key
            default: Default value if key not found

        Returns:
            The configuration value
        """
        return self._config.get(key, default)

    def get_port(self, default: int = 5001) -> int:
        """
        Get the port from configuration.

        Args:
            default: Default port if not configured

        Returns:
            The port number
        """
        port_value = self.get("port")

        if port_value is None or port_value == "null":
            return default

        return int(port_value)

    def get_database_uri(self, basedir: str) -> str:
        """
        Get the database URI.

        Args:
            basedir: Base directory for relative database paths

        Returns:
            The database URI
        """
        db_path = self.get("database_path", "instance/usergazetrack.db")

        if not os.path.isabs(db_path):
            db_path = os.path.join(basedir, db_path)

        return f"sqlite:///{db_path}"

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary of all configuration
        """
        return self._config.copy()

    def get_tasks(self) -> Dict[str, Any]:
        """
        Get all tasks configuration.

        Returns:
            Dictionary of all tasks
        """
        return self._tasks.copy()

    def print_config(self) -> None:
        """Print configuration values to console."""
        print("Configuration:")
        for key, value in self._config.items():
            print(f"  - {key}: {value}")
