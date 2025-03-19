"""
Unit tests for get_vpn_connector in dependencies/vpn_manager_fabric.py.
We mock platform.system() to return 'Windows' / 'Darwin' / 'Linux' etc.,
and check that the correct connector is instantiated or exception is raised.
"""

import platform
from unittest.mock import patch

import pytest

from core.managers.vpn_manager_macos import MacOSL2TPConnector
from core.managers.vpn_manager_win import WindowsL2TPConnector
from dependencies.vpn_manager_fabric import get_vpn_connector


def test_get_vpn_connector_windows():
    """
    If platform.system().lower() == 'windows', we expect a WindowsL2TPConnector instance.
    """
    with patch("platform.system", return_value="Windows"):
        connector = get_vpn_connector()
        assert isinstance(connector, WindowsL2TPConnector)


def test_get_vpn_connector_macos():
    """
    If platform.system().lower() == 'darwin', we expect a MacOSL2TPConnector instance.
    """
    with patch("platform.system", return_value="Darwin"):
        connector = get_vpn_connector()
        assert isinstance(connector, MacOSL2TPConnector)


def test_get_vpn_connector_linux():
    """
    If platform.system().lower() == 'linux', we expect NotImplementedError for now.
    """
    with patch("platform.system", return_value="Linux"):
        with pytest.raises(NotImplementedError, match="Linux not implemented yet"):
            get_vpn_connector()


def test_get_vpn_connector_unknown():
    """
    If platform.system().lower() returns something else, raise NotImplementedError.
    """
    with patch("platform.system", return_value="Solaris"):
        with pytest.raises(NotImplementedError, match="Unsupported OS: solaris"):
            get_vpn_connector()
