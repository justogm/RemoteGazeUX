"""
Tests for state/config management.
"""

import pytest
import os
import json
import tempfile
from state.config_manager import ConfigManager


class TestConfigManager:
    """Tests for ConfigManager class."""

    def test_create_config_manager(self):
        """Test creating a config manager."""
        manager = ConfigManager()
        assert manager is not None
        assert hasattr(manager, "_config")
        assert isinstance(manager._config, dict)
        assert hasattr(manager, "_tasks")
        assert isinstance(manager._tasks, dict)

    def test_load_config_from_file(self):
        """Test loading config from file."""
        # Create a temporary config directory
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            config_data = {
                "url_path": "https://test.com",
                "img_path": "/test/image.png",
                "port": 5002,
            }

            with open(config_file, "w") as f:
                json.dump(config_data, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_config()

            assert manager.get("url_path") == "https://test.com"
            assert manager.get("img_path") == "/test/image.png"
            assert manager.get("port") == 5002

    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(config_dir=temp_dir)

            with pytest.raises(FileNotFoundError):
                manager.load_config()

    def test_get_with_default(self):
        """Test getting config value with default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            with open(config_file, "w") as f:
                json.dump({"key1": "value1"}, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_config()

            # Existing key
            assert manager.get("key1") == "value1"

            # Non-existent key with default
            assert manager.get("non_existent", "default") == "default"

    def test_get_port_with_default(self):
        """Test getting port with default value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")

            # No port in config
            with open(config_file, "w") as f:
                json.dump({}, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_config()

            port = manager.get_port(default=5000)
            assert port == 5000

    def test_get_port_from_config(self):
        """Test getting port from configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            with open(config_file, "w") as f:
                json.dump({"port": 8080}, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_config()

            port = manager.get_port()
            assert port == 8080

    def test_get_port_null_value(self):
        """Test getting port when value is 'null' string."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            with open(config_file, "w") as f:
                json.dump({"port": "null"}, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_config()

            port = manager.get_port(default=5001)
            assert port == 5001

    def test_get_all(self):
        """Test getting all configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            config_data = {"key1": "value1", "key2": "value2"}

            with open(config_file, "w") as f:
                json.dump(config_data, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_config()

            all_config = manager.get_all()
            assert all_config == config_data

    def test_print_config(self, capsys):
        """Test printing config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            with open(config_file, "w") as f:
                json.dump({"url_path": "https://test.com"}, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_config()
            manager.print_config()

            captured = capsys.readouterr()
            assert "Configuration:" in captured.out
            assert "url_path" in captured.out

    def test_load_tasks(self):
        """Test loading tasks configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_file = os.path.join(temp_dir, "tasks.json")
            tasks_data = {"task1": {"type": "test"}}

            with open(tasks_file, "w") as f:
                json.dump(tasks_data, f)

            manager = ConfigManager(config_dir=temp_dir)
            tasks = manager.load_tasks()

            assert tasks == tasks_data

    def test_get_tasks(self):
        """Test getting all tasks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_file = os.path.join(temp_dir, "tasks.json")
            tasks_data = {"task1": {"type": "test"}}

            with open(tasks_file, "w") as f:
                json.dump(tasks_data, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_tasks()

            all_tasks = manager.get_tasks()
            assert all_tasks == tasks_data

    def test_get_database_uri(self):
        """Test getting database URI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            with open(config_file, "w") as f:
                json.dump({"database_path": "instance/test.db"}, f)

            manager = ConfigManager(config_dir=temp_dir)
            manager.load_config()

            uri = manager.get_database_uri("/home/test")
            assert uri.startswith("sqlite:///")
            assert "instance/test.db" in uri


class TestConfigManagerEdgeCases:
    """Tests for edge cases in ConfigManager."""

    def test_load_tasks_file_not_found(self):
        """Test loading non-existent tasks file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(config_dir=temp_dir)

            with pytest.raises(FileNotFoundError):
                manager.load_tasks()

    def test_invalid_json_file(self):
        """Test loading invalid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")
            with open(config_file, "w") as f:
                f.write('{"invalid": json content}')

            manager = ConfigManager(config_dir=temp_dir)

            with pytest.raises(json.JSONDecodeError):
                manager.load_config()

    def test_default_config_dir(self):
        """Test that default config dir is set correctly."""
        manager = ConfigManager()
        assert manager.config_dir is not None
        assert os.path.isabs(manager.config_dir)
