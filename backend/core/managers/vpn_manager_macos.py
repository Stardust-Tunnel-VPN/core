# core/services/managers/vpn_manager_macos.py

"""
Python module for managing VPN connections on macOS.
"""

import asyncio
import logging
from typing import Optional

from configuration.macos_l2tp_connection import (
    extract_ip_address_from_service_name, open_macos_network_settings)
from core.interfaces.ivpn_connector import IVpnConnector

logger = logging.getLogger(__name__)


class MacOSL2TPConnector(IVpnConnector):
    """
    For macOS:
      - We can open System Settings -> Network to let user manually create an L2TP service.
      - If the user has already created a service named self.service_name (e.g. "MyL2TP"),
        we can connect/disconnect using `scutil --nc start/stop`.
         (Unfortunately, we can't establish it fully programmatically. Apple doesn't allow it. We can only create a connection manually in the System Settings -> Network pane and after that connect to it programmatically, that's the only way for 09.03.2025)

    METHODS THAT SHOULD BE IMPLEMENTED ACCORDING TO IVpnConnector:
    - connect ✅
    - disconnect ✅
    - status ✅
    - enable_kill_switch ✅ (not tested yet)
    - disable_kill_switch ✅ (not tested yet)
    """

    def __init__(self, service_name: str = "MyL2TP"):
        self.service_name = service_name
        self.service_psk_value = "vpn"
        self.current_vpn_ip: Optional[str] = None

    # TODO: extract repeated vars to reusable-utils

    async def connect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> None:
        """
        VPN Class method to connect to a VPN server using L2TP/IPsec protocol on macOS.

        Raises:
            RuntimeError: If the connection fails.
        """
        try:
            # OPENING NETWORK SETTINGS #
            logger.info("macOS: Opening Network Settings to let the user configure L2TP.")
            await open_macos_network_settings()

            # CONNECTION TO 'MYL2TP' SERVICE #
            cmd = ["scutil", "--nc", "start", self.service_name, "--secret", self.service_psk_value]

            logger.info(f"Trying to start L2TP service '{self.service_name}' for IP={server_ip}")

            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            self.current_vpn_ip = await extract_ip_address_from_service_name(self.service_name)

            if proc.returncode != 0:
                err = stderr.decode().strip()
                msg = (
                    f"Failed to start VPN on macOS: {err}. "
                    "Make sure you've created the L2TP service in System Settings -> Network."
                )
                raise RuntimeError(msg)

            logger.info(f"Connected to {server_ip} via L2TP: {stdout.decode().strip()}")
        except Exception as exc:
            logger.error(f"Failed to connect to {server_ip} on macOS: {exc}")
            raise exc

    async def disconnect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> None:
        """
        Class method to disconnect from a VPN server on macOS.

        Raises:
            RuntimeError: If the disconnection fails.
        """
        try:
            # DISCONNECTING FROM 'MYL2TP' SERVICE #
            cmd = ["scutil", "--nc", "stop", self.service_name]

            logger.info(
                f"Stopping L2TP service '{self.service_name}' for IP={server_ip} with scutil."
            )

            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err = stderr.decode().strip()
                raise RuntimeError(f"Failed to stop VPN on macOS: {err}")

            logger.info(
                f"Disconnected VPN '{self.service_name}' from {server_ip}. Output: {stdout.decode().strip()}"
            )
        except Exception as exc:
            logger.error(f"Failed to disconnect from {server_ip}: {exc}")
            raise

    async def status(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Class method to check the status of a VPN connection on macOS.

        Returns:
            str: The status of the VPN connection.
        """
        try:
            # CHECKING STATUS OF 'MYL2TP' SERVICE #
            cmd = ["scutil", "--nc", "status", self.service_name]

            logger.info(f"Checking VPN status on macOS: {cmd}")
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await proc.communicate()
            output = stdout.decode().lower()

            if "disconnected" in output:
                return "disconnected"
            elif "connected" in output:
                return "connected"
            else:
                return "unknown"
        except Exception as exc:
            logger.error(f"Failed to check status on macOS: {exc}")
            return "unknown"

    async def enable_kill_switch(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> None:
        """
        Class method to enable a kill switch on macOS.

        Raises:
            RuntimeError: If the kill switch fails to enable.
        """
        try:
            # ENABLE KILL SWITCH (MACOS)#
            
        except Exception as exc:
            logger.error(f"Failed to enable kill switch on macOS: {exc}")
            raise exc

    async def disable_kill_switch(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> None:
        """
        Class method to disable a kill switch on macOS.

        Raises:
            RuntimeError: If the kill switch fails to disable.
        """
        try:
            # DISABLE KILL SWITCH (MACOS)#
            
        except Exception as exc:
            logger.error(f"Failed to disable kill switch on macOS: {exc}")
            raise exc
