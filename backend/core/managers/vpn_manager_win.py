# core/services/managers/vpn_manager_win.py

"""
VPN Manager module for Windows OS.
"""

import asyncio
import logging
from typing import Optional

from configuration.win_l2tp_connection import create_windows_l2tp
from core.interfaces.ivpn_connector import IVpnConnector

logger = logging.getLogger(__name__)


class WindowsL2TPConnector(IVpnConnector):
    """
    Use rasdial for connect/disconnect,
    and netsh advfirewall for kill switch.
    """

    def __init__(self, connection_name: str = "MyL2TP"):
        self.connection_name = connection_name

    async def connect(
        self,
        server_ip: str,
        username: str = "vpn",
        password: str = "vpn",
        psk: str = "vpn",
    ) -> None:
        """
        Windows connector class method that connects to a VPN server using L2TP/IPsec protocol.

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
            await create_windows_l2tp(server_ip, name=self.connection_name, psk=psk)

            # CONNECTION #
            cmd = ["rasdial", connection_name, username, password]
            logger.info(
                f"WindowsL2TPConnector: connecting to {server_ip} with cmd: {cmd}"
            )

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(
                    f"rasdial failed: {stderr.decode('utf-8', errors='ignore')}"
                )
                raise RuntimeError(
                    f"rasdial failed: {stderr.decode('utf-8', errors='ignore')}"
                )

        except Exception as exc:
            logger.error(f"Failed to connect to {server_ip}: {exc}")
            raise exc

    async def disconnect(self, server_ip: str) -> None:
        """
        Windows connector class method that disconnects from a VPN server.

        Args:
            server_ip (str): The IP address of the VPN server.

        Raises:
            RuntimeError: If the disconnection fails.
        """
        try:
            # DISCONNECT #
            cmd = ["rasdial", self.connection_name, "/disconnect"]
            logger.info(
                f"WindowsL2TPConnector: disconnecting from {server_ip} with cmd: {cmd}"
            )
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            _, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"rasdial /disconnect failed: {stderr.decode()}")
                raise RuntimeError(f"rasdial /disconnect failed: {stderr.decode()}")

        except Exception as exc:
            logger.error(f"Failed to disconnect from {server_ip}: {exc}")
            raise exc

    async def status(self, server_ip: str) -> str:
        """
        Windows connector class method that checks the current status of the VPN connection.

        Args:
            server_ip (str): The IP address of the VPN server.

        Returns:
            str: The status of the VPN connection.
        """
        try:

            # STATUS #
            cmd = ["rasdial"]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await process.communicate()

            output = stdout.decode().lower()

            if (
                self.connection_name.lower in output
                and "command completed successfully" in output
            ):
                return "connected"
            else:
                return "disconnected"

        except Exception as exc:
            logger.error(f"Failed to get status for {server_ip}: {exc}")
            raise exc

    async def enable_kill_switch(self, server_ip: str) -> None:
        """
        Block all outbound traffic except for the VPN server IP.
        This is a naive example.

        Args:
            server_ip (str): The IP address of the VPN server.

        Raises:
            Exception: If the kill switch fails to enable.
        """
        try:
            logger.info(f"Enabling kill switch on Windows for {server_ip}...")

            # TODO: extract this to a separate variable
            block_cmd = [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                "name=KillSwitchBlockAll",
                "dir=out",
                "action=block",
                "remoteip=0.0.0.0/0",
            ]

            process = await asyncio.create_subprocess_exec(*block_cmd)
            await process.communicate()

            allow_cmd = [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                "name=KillSwitchAllowVPN",
                "dir=out",
                "action=allow",
                f"remoteip={server_ip}",
            ]

            process = await asyncio.create_subprocess_exec(*allow_cmd)
            await process.communicate()

        except Exception as exc:
            logger.error(f"Failed to enable kill switch: {exc}")
            raise

    async def disable_kill_switch(self, server_ip: str) -> None:
        """
        Remove or disable the firewall rules.

        Args:
            server_ip (str): The IP address of the VPN server.

        Raises:
            Exception: If the kill switch fails to disable.
        """
        try:
            logger.info(f"Disabling kill switch on Windows (example).")

            # TODO: extract this to a separate variable
            remove_block = [
                "netsh",
                "advfirewall",
                "firewall",
                "delete",
                "rule",
                "name=KillSwitchBlockAll",
            ]

            proc = await asyncio.create_subprocess_exec(*remove_block)
            await proc.communicate()

            remove_allow = [
                "netsh",
                "advfirewall",
                "firewall",
                "delete",
                "rule",
                "name=KillSwitchAllowVPN",
            ]

            proc = await asyncio.create_subprocess_exec(*remove_allow)
            await proc.communicate()

        except Exception as exc:
            logger.error(f"Failed to disable kill switch: {exc}")
            raise
