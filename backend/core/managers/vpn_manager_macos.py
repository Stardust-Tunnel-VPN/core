# core/services/managers/vpn_manager_macos.py

import asyncio
import logging
import os
import uuid
from typing import Optional

from configuration.macos_l2tp_connection import create_macos_l2tp_service
from core.interfaces.ivpn_connector import IVpnConnector

logger = logging.getLogger(__name__)


class MacOSL2TPConnector(IVpnConnector):
    """
    Use 'scutil --nc start/stop' for connect/disconnect.
    PF for kill switch.
    Also create a .mobileconfig if not installed yet.
    """

    def __init__(self, service_name: str = "MyL2TP"):
        self.service_name = service_name

    async def connect(
        self, server_ip: str, username: str = "vpn", password: str = "vpn", psk: str = "vpn"
    ) -> None:
        """
        MacOS connector class method that connects to a VPN server using L2TP/IPsec protocol.

        Args:
            server_ip (str): The IP address of the VPN server.
            username (str): The username for the VPN connection. Defaults to "vpn".
            password (str): The password for the VPN connection. Defaults to "vpn".
            psk (str): The pre-shared key for the connection. Defaults to "vpn".

        Raises:
            RuntimeError: If the connection fails.
        """
        try:
            # CREATE VPN PROFILE #
            await create_macos_l2tp_service(server_ip, self.service_name, psk, username, password)

            # CONNECT WITH SCUTIL #
            cmd = ["scutil", "--nc", "start", self.service_name]
            logger.info(
                f"MacOSL2TPConnector: starting service '{self.service_name}' for {server_ip} with scutil."
            )

            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err = stderr.decode()
                raise RuntimeError(f"Failed to start VPN on macOS: {err}")

            logger.info(f"Connected to {server_ip} via L2TP: {stdout.decode().strip()}")

        except Exception as exc:
            logger.error(f"Failed to connect to {server_ip} on macOS: {exc}")
            raise

    async def disconnect(self, server_ip: str) -> None:
        """
        MacOS connector class method that disconnects from a VPN server.

        Args:
            server_ip (str): The IP address of the VPN server.

        Raises:
            RuntimeError: If the disconnection fails.
        """
        try:

            # DISCONNECT WITH SCUTIL #
            cmd = ["scutil", "--nc", "stop", self.service_name]

            logger.info(
                f"MacOSL2TPConnector: stopping service '{self.service_name}' for {server_ip} with scutil."
            )

            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err = stderr.decode()
                raise RuntimeError(f"Failed to stop VPN on macOS: {err}")

            logger.info(
                f"Disconnected VPN '{self.service_name}' from {server_ip}. Output: {stdout.decode().strip()}"
            )

        except Exception as exc:
            logger.error(f"Failed to disconnect from {server_ip}: {exc}")
            raise

    async def status(self, server_ip: str) -> str:
        """
        MacOS connector class method that checks the current status of the VPN connection.

        Args:
            server_ip (str): The IP address of the VPN server.

        Returns:
            str: The status of the VPN connection.
        """
        try:
            cmd = ["scutil", "--nc", "status", self.service_name]

            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await proc.communicate()

            output = stdout.decode().lower()

            if "connected" in output:
                return "connected"
            return "disconnected"

        except Exception as exc:
            logger.error(f"Failed to check status on macOS: {exc}")
            return "unknown"

    # async def enable_kill_switch(self, server_ip: str) -> None:
    #     """
    #     Example usage of pfctl.
    #     In real scenario, we'd place a PF config that blocks all except the VPN server and ppp0/utunX.
    #     """
    #     try:
    #         logger.info(f"Enabling kill switch on macOS for server {server_ip} (dummy).")
    #         cmd_enable_pf = ["sudo", "pfctl", "-e"]
    #         proc = await asyncio.create_subprocess_exec(*cmd_enable_pf)
    #         await proc.communicate()

    #         # Additional steps (like writing /etc/pf.anchors/killvpn.conf and reloading).
    #     except Exception as exc:
    #         logger.error(f"Failed to enable kill switch on macOS: {exc}")
    #         raise

    # async def disable_kill_switch(self, server_ip: str) -> None:
    #     try:
    #         logger.info(f"Disabling kill switch on macOS.")
    #         cmd_disable_pf = ["sudo", "pfctl", "-d"]
    #         proc = await asyncio.create_subprocess_exec(*cmd_disable_pf)
    #         await proc.communicate()
    #     except Exception as exc:
    #         logger.error(f"Failed to disable kill switch on macOS: {exc}")
    #         raise
