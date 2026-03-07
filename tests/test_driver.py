"""Unit tests for Molecule Lima Driver."""

import pytest
from unittest.mock import MagicMock, patch

from molecule import api
from molecule_lima.driver import Lima


def test_lima_driver_is_detected(DRIVER):
    """Asserts that molecule recognizes the driver."""
    assert DRIVER in [str(d) for d in api.drivers()]


def test_driver_name():
    """Test that the driver has the correct default name."""
    driver = Lima()
    assert driver.name == "molecule-lima"


def test_driver_name_setter():
    """Test that the driver name can be set."""
    driver = Lima()
    driver.name = "custom-lima"
    assert driver.name == "custom-lima"


def test_driver_delegated_property():
    """Test that delegated property returns False."""
    driver = Lima()
    assert driver.delegated is False


def test_driver_managed_property():
    """Test that managed property returns True."""
    driver = Lima()
    assert driver.managed is True


def test_driver_login_cmd_template():
    """Test that login command template is correct."""
    driver = Lima()
    assert driver.login_cmd_template == "limactl shell {instance}"


def test_driver_default_ssh_connection_options():
    """Test that default SSH connection options are correct."""
    driver = Lima()
    expected = [
        "-o UserKnownHostsFile=/dev/null",
        "-o StrictHostKeyChecking=no",
        "-o IdentitiesOnly=yes",
    ]
    assert driver.default_ssh_connection_options == expected


def test_driver_required_collections():
    """Test that required_collections returns correct collections."""
    driver = Lima()
    expected = {"community.general": "9.0.0"}
    assert driver.required_collections == expected


def test_driver_initializes_without_limactl_executable(monkeypatch):
    """Make sure we can initialize driver without having limactl executable present."""
    monkeypatch.setenv("MOLECULE_LIMA_EXECUTABLE", "bad-executable")
    Lima()


def test_driver_sanity_check_fails_without_limactl(monkeypatch):
    """Test that sanity_check fails when limactl is not found."""
    monkeypatch.setattr("molecule_lima.driver.which", lambda x: None)
    mock_config = MagicMock()
    driver = Lima(config=mock_config)
    with pytest.raises(SystemExit):
        driver.sanity_checks()


def test_driver_sanity_check_passes_with_limactl(monkeypatch):
    """Test that sanity_check passes when limactl is found."""
    monkeypatch.setattr("molecule_lima.driver.which", lambda x: x == "limactl")
    mock_config = MagicMock()
    driver = Lima(config=mock_config)
    driver.sanity_checks()


def test_login_options_returns_instance_name():
    """Test that login_options returns instance name in dict."""
    mock_config = MagicMock()
    driver = Lima(config=mock_config)
    with patch("molecule_lima.driver.util.safe_load_file", side_effect=OSError):
        result = driver.login_options("test-instance")
    assert result == {"instance": "test-instance"}


def test_ansible_connection_options_returns_empty_when_no_config():
    """Test that ansible_connection_options returns empty dict when no config."""
    mock_config = MagicMock()
    mock_config.driver.instance_config = "/path/to/config"
    driver = Lima(config=mock_config)
    with patch("molecule_lima.driver.util.safe_load_file", side_effect=OSError):
        result = driver.ansible_connection_options("test-instance")
    assert result == {}


def test_ansible_connection_options_returns_correct_options():
    """Test that ansible_connection_options returns correct SSH options."""
    mock_config = MagicMock()
    mock_config.driver.instance_config = "/path/to/config"
    driver = Lima(config=mock_config)

    mock_instance_data = [
        {
            "instance": "test-instance",
            "user": "root",
            "address": "192.168.1.100",
            "port": 22,
            "identity_file": "/path/to/key"
        }
    ]

    with patch("molecule_lima.driver.util.safe_load_file", return_value=mock_instance_data):
        result = driver.ansible_connection_options("test-instance")

    assert result["ansible_user"] == "root"
    assert result["ansible_host"] == "192.168.1.100"
    assert result["ansible_port"] == 22
    assert result["ansible_ssh_private_key_file"] == "/path/to/key"
    assert result["ansible_connection"] == "ssh"
    assert "ansible_ssh_common_args" in result


def test_status_returns_list():
    """Test that status returns a list of Status objects."""
    mock_config = MagicMock()
    mock_config.platforms.instances = [{"name": "test-instance"}]
    mock_config.provisioner = MagicMock()
    mock_config.provisioner.name = "ansible"
    mock_config.scenario.name = "default"
    mock_config.state.created = True
    mock_config.state.converged = False

    driver = Lima(config=mock_config)
    result = driver.status()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].instance_name == "test-instance"
    assert result[0].driver_name == "molecule-lima"


def test_status_handles_empty_instances():
    """Test that status handles empty instances list."""
    mock_config = MagicMock()
    mock_config.platforms.instances = []
    mock_config.provisioner = MagicMock()
    mock_config.provisioner.name = "ansible"
    mock_config.scenario.name = "default"
    mock_config.state.created = True
    mock_config.state.converged = False

    driver = Lima(config=mock_config)
    result = driver.status()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].instance_name == ""


def test_testinfra_options_returns_empty_when_no_provisioner():
    """Test that testinfra_options returns empty dict when no provisioner."""
    mock_config = MagicMock()
    mock_config.provisioner = None

    driver = Lima(config=mock_config)
    result = driver.testinfra_options

    assert result == {}


def test_testinfra_options_returns_correct_options():
    """Test that testinfra_options returns correct options."""
    mock_config = MagicMock()
    mock_config.provisioner = MagicMock()
    mock_config.provisioner.inventory_file = "/path/to/inventory"

    driver = Lima(config=mock_config)
    result = driver.testinfra_options

    assert result["connection"] == "ansible"
    assert result["ansible-inventory"] == "/path/to/inventory"


def test_default_safe_files():
    """Test that default_safe_files returns instance_config."""
    mock_config = MagicMock()
    mock_config.driver.instance_config = "/path/to/instance_config.yml"
    mock_config.scenario.ephemeral_directory = "/tmp/molecule"
    driver = Lima(config=mock_config)
    result = driver.default_safe_files
    assert len(result) == 1
    assert "instance_config" in result[0]


def test_schema_file_returns_none_when_no_schema():
    """Test that schema_file returns None when schema.json doesn't exist."""
    mock_config = MagicMock()
    mock_config.scenario.ephemeral_directory = "/tmp/molecule"
    driver = Lima(config=mock_config)
    with patch("pathlib.Path.is_file", return_value=False):
        result = driver.schema_file()
    assert result is None


def test_schema_file_returns_path_when_schema_exists():
    """Test that schema_file returns path when schema.json exists."""
    mock_config = MagicMock()
    mock_config.scenario.ephemeral_directory = "/tmp/molecule"
    driver = Lima(config=mock_config)
    with patch("pathlib.Path.is_file", return_value=True):
        result = driver.schema_file()
    assert result is not None
    assert "schema.json" in result


def test_ansible_connection_options_returns_empty_on_stop_iteration():
    """Test ansible_connection_options returns empty when instance not found."""
    mock_config = MagicMock()
    mock_config.driver.instance_config = "/path/to/config"
    driver = Lima(config=mock_config)
    with patch("molecule_lima.driver.util.safe_load_file", return_value=[]):
        result = driver.ansible_connection_options("nonexistent")
    assert result == {}


def test_login_options_merges_instance_config():
    """Test login_options merges instance config with instance name."""
    mock_config = MagicMock()
    mock_config.driver.instance_config = "/path/to/config"
    driver = Lima(config=mock_config)

    mock_instance_data = [
        {
            "instance": "test-instance",
            "user": "ubuntu",
            "address": "192.168.1.50",
            "port": 22,
            "identity_file": "/home/user/.ssh/id_rsa"
        }
    ]

    with patch("molecule_lima.driver.util.safe_load_file", return_value=mock_instance_data):
        result = driver.login_options("test-instance")

    assert result["instance"] == "test-instance"
    assert result["user"] == "ubuntu"
    assert result["address"] == "192.168.1.50"
