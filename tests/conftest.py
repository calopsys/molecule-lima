"""Pytest Fixtures for Molecule Lima Driver Tests."""

import pytest

@pytest.fixture()
def DRIVER():
    """Return name of the driver to be tested."""
    return "molecule-lima"
