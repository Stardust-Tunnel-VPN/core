"""
Python module that returns correct VPN Manager class instance depending on the OS of current user.
"""

from platform import system

from fastapi import Depends

from core.interfaces.ivpn_connector import IVpnConnector
from core.managers.vpn_manager_macos import MacOSL2TPConnector
from core.managers.vpn_manager_win import WindowsL2TPConnector
from utils.reusable.vpn_implementations import VpnImplementation


def get_vpn_connector() -> IVpnConnector:
    """
    Auto-detect the current OS using platform.system(),
    and return the appropriate VPN manager instance.

    Returns:
        IVpnConnector: An instance of a VPN manager class.
    """
    try:
        os_name = platform.system().lower()  # e.g. 'windows', 'darwin', 'linux'
        if os_name == "windows":
            return WindowsL2TPConnector()
        elif os_name == "darwin":
            return MacOSL2TPConnector()
        elif os_name == "linux":
            raise NotImplementedError("Linux not implemented yet")
        else:
            raise NotImplementedError(f"Unsupported OS: {os_name}")
    except Exception as exc:
        print(f"Failed to get correct VPN connector in vpn manager fabric: {exc}")
        raise exc
