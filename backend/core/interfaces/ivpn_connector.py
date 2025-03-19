import asyncio
from typing import Optional, Protocol

"""
Python module that represents the general interface for any L2TP/IPSec protocol VPN connector. 
Implementations of this interface should be able to connect, disconnect, check status, enable/disable kill switch. Supported OS: Windows, macOS, Linux, Android, iOS.
"""


class IVpnConnector(Protocol):
    """
    Interface/Protocol describing the methods needed
    for any L2TP/IPSec connector on different OS.
    """

    async def connect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
        kill_switch_enabled: Optional[bool] = False,
    ) -> str:
        """
        Asynchronously connect to the given VPN server using L2TP/IPSec.
        :param server_ip: The VPN server IP or hostname.
        :param username: Typically 'vpn'
        :param password: Typically 'vpn'
        :param psk: Pre-shared key for IPSec, typically 'vpn'
        :param kill_switch_enabled: Enable kill switch blocking all traffic outside VPN
        :raises Exception: if failed
        """
        ...

    async def disconnect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Asynchronously disconnect from the given VPN server.
        :param server_ip: The VPN server IP or name used previously
        :raises Exception: if failed
        """
        ...

    async def status(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Check if the given server is connected or not.
        :returns: 'connected', 'disconnected', or 'unknown'
        """
        ...

    async def enable_kill_switch(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Enable kill switch, blocking all traffic outside VPN.
        """
        ...

    async def disable_kill_switch(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Disable kill switch, restore normal network.
        """
        ...
