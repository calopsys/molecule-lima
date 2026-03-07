# Agent Guidelines for molecule-lima

This file provides guidelines for agents working on the molecule-lima project.

## Project Overview

molecule-lima is a Molecule driver for Lima VM, enabling testing of Ansible roles on Linux with native virtualization support.

## Build, Lint, and Test Commands

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
pip install -e ".[lint]"  # For linting
pip install -e ".[test]"   # For testing
pip install pytest-cov    # For coverage
```

### Running Commands

```bash
# Install package in editable mode
pip install -e .

# Run all tests
pytest tests/ -v

# Run a single test
pytest tests/test_driver.py::test_driver_name -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/

# Run both lint and type check
ruff check src/ tests/ && mypy src/
```

### CI/CD

The project uses GitHub Actions (`.github/workflows/ci.yml`):
- Lint job: runs `ruff check` and `mypy`
- Test job: runs `pytest tests/`

## Code Style Guidelines

### General Principles

- Write clean, readable, and maintainable code
- Follow existing patterns in the codebase
- Keep functions focused and small (single responsibility)
- Add docstrings to all public methods

### Python Version

- Minimum Python 3.13
- Use type hints throughout
- Use `from __future__ import annotations` for forward references

### Imports

```python
# Standard library first
import os
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, Any

# Third-party imports
from molecule import logger, util
from molecule.api import Driver
from molecule.status import Status

# Local imports (if applicable)
# from molecule_lima import something

# TYPE_CHECKING block for type-only imports
if TYPE_CHECKING:
    from molecule.config import Config
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `class Lima`)
- **Functions/methods**: `snake_case` (e.g., `def login_options`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT = 30`)
- **Private methods**: prefix with `_` (e.g., `_get_instance_config`)
- **Variables**: `snake_case` (e.g., `instance_name`)

### Type Hints

```python
# Use type hints for all function signatures
def __init__(self, config: Config | None = None) -> None:
    ...

def login_options(self, instance_name: str) -> dict[str, str]:
    ...

@property
def required_collections(self) -> dict[str, str]:
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def login_options(self, instance_name: str) -> dict[str, str]:
    """Return login options for instance.

    Args:
        instance_name: Name of the instance.

    Returns:
        Dictionary with login options including instance name and SSH details.
    """
```

### Error Handling

- Use specific exception types
- Handle expected errors gracefully
- Let unexpected errors propagate

```python
def login_options(self, instance_name: str) -> dict[str, str]:
    d = {"instance": instance_name}
    try:
        return util.merge_dicts(d, self._get_instance_config(instance_name))
    except (StopIteration, OSError):
        return d
```

### Properties

Use `@property` decorator for computed attributes:

```python
@property
def name(self) -> str:
    """Return driver name."""
    return self._name

@name.setter
def name(self, value: str) -> None:
    """Set driver name."""
    self._name = value
```

### Testing Guidelines

- Test file naming: `test_<module_name>.py`
- Test class naming: `Test<ClassName>`
- Test function naming: `test_<description>`
- Use `unittest.mock.MagicMock` for mocking
- Use `monkeypatch` for environment manipulation
- Aim for high test coverage (currently 100%)

```python
def test_driver_name():
    """Test that the driver has the correct default name."""
    driver = Lima()
    assert driver.name == "molecule-lima"
```

### Driver Implementation Pattern

When implementing a Molecule driver, follow this pattern:

```python
class Lima(Driver):
    default_name = "molecule-lima"

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)  # type: ignore[arg-type]
        self._name = self.default_name

    # Required properties
    @property
    def name(self) -> str: ...
    @property
    def delegated(self) -> bool: ...
    @property
    def managed(self) -> bool: ...
    @property
    def login_cmd_template(self) -> str: ...
    @property
    def default_ssh_connection_options(self) -> list[str]: ...
    @property
    def default_safe_files(self) -> list[str]: ...

    # Required methods
    def login_options(self, instance_name: str) -> dict[str, str]: ...
    def ansible_connection_options(self, instance_name: str) -> dict[str, Any]: ...
    def status(self) -> list[Status]: ...
    def sanity_checks(self) -> None: ...

    # Optional methods
    def schema_file(self) -> str | None: ...
```

### File Organization

```text
src/molecule_lima/
  __init__.py       # Package init, version, exports
  driver.py         # Main driver implementation

tests/
  __init__.py       # Test package
  conftest.py       # Pytest fixtures
  test_driver.py    # Driver unit tests
```

### Pre-commit Checks

Before committing, always run:

```bash
ruff check src/ tests/
mypy src/
pytest tests/ -v
```

### Adding New Features

1. Write tests first (TDD approach recommended)
2. Implement the feature
3. Ensure all tests pass
4. Run lint and type checks
5. Update documentation if needed

### Common Patterns

**Config access**:
```python
self._config.driver.instance_config
self._config.platforms.instances
self._config.provisioner.inventory_file
self._config.scenario.ephemeral_directory
```

**SSH connection options**:
```python
def default_ssh_connection_options(self) -> list[str]:
    return [
        "-o UserKnownHostsFile=/dev/null",
        "-o StrictHostKeyChecking=no",
        "-o IdentitiesOnly=yes",
    ]
```
