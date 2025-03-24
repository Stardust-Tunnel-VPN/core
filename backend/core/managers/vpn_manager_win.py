# core/services/managers/vpn_manager_win.py

import subprocess
import logging
import asyncio
from typing import Optional

from configuration.win_l2tp_connection import create_windows_l2tp
from core.interfaces.ivpn_connector import IVpnConnector
from utils.reusable.commands.windows.reusable_commands_map import cmds_map_windows

logger = logging.getLogger(__name__)


class WindowsL2TPConnector(IVpnConnector):
    """
    Use rasdial for connect/disconnect,
    and netsh advfirewall for kill switch.
    """

    def __init__(self, connection_name: str = "MyL2TP"):
        self.connection_name = connection_name

    def _connect_sync(
        self,
        server_ip: str,
        username: str,
        password: str,
        psk: str,
        kill_switch_enabled: bool = False,
    ) -> str:
        try:
            if not server_ip:
                raise ValueError("server_ip cannot be None or empty.")

            create_windows_l2tp(server_ip=server_ip, name=self.connection_name, psk=psk)

            # TODO: extract to a separate method/function
            cmd = cmds_map_windows["connect_to_l2tp_service"][:]
            final_username = username or "vpn"
            final_password = password or "vpn"
            cmd += [self.connection_name, final_username, final_password]

            if kill_switch_enabled:
                self.enable_kill_switch(server_ip)

            logger.info(f"WindowsL2TPConnector: connecting with command: {cmd}")

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"rasdial failed: {result.stdout or result.stderr}")

            return f"Connected to {server_ip} successfully."

        except Exception as exc:
            logger.error(f"Failed to connect to {server_ip}: {exc}")
            raise exc

    async def connect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = "vpn",
        password: Optional[str] = "vpn",
        psk: Optional[str] = "vpn",
        kill_switch_enabled: bool = False,
    ) -> str:
        try:

            if kill_switch_enabled:
                self.enable_kill_switch(server_ip)

            return await asyncio.to_thread(
                self._connect_sync, server_ip, username, password, psk, kill_switch_enabled
            )

        except Exception as exc:
            logger.error(f"Failed to connect to {server_ip}: {exc}")
            raise exc

    def _disconnect_sync(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Disconnect from the VPN.
        """
        try:
            # TODO: extract to a separate method/function
            cmd = cmds_map_windows["disconnect_from_l2tp_service"][:]
            cmd += [self.connection_name]

            logger.info(f"WindowsL2TPConnector: disconnecting from {server_ip} with cmd: {cmd}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"rasdial /disconnect failed: {result.stdout or result.stderr}")

            return f"Disconnected from {server_ip} successfully."

        except Exception as exc:
            logger.error(f"Failed to disconnect from {server_ip}: {exc}")
            raise exc

    async def disconnect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        try:
            return await asyncio.to_thread(
                self._disconnect_sync, server_ip, username, password, psk
            )
        except Exception as exc:
            logger.error(f"Failed to disconnect from {server_ip}: {exc}")
            raise exc

    def _status_check_sync(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Check if the VPN connection is active or not.
        """
        try:
            # TODO: extract to a separate method/function
            cmd = cmds_map_windows["check_connection_status"][:]
            cmd += [self.connection_name]

            result = subprocess.run(cmd, capture_output=True, text=True)

            output = result.stdout.lower()

            if (
                self.connection_name.lower() in output
                and "command completed successfully" in output
            ):
                return (
                    f"Connected to {self.connection_name} successfully. Connection IP: {server_ip}"
                )
            else:
                return f"Disconnected"
        except Exception as exc:
            logger.error(f"Failed to get status for {server_ip}: {exc}")
            raise exc

    async def status(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        try:
            return await asyncio.to_thread(
                self._status_check_sync, server_ip, username, password, psk
            )
        except Exception as exc:
            logger.error(f"Failed to get status for {server_ip}: {exc}")
            raise exc

    def enable_kill_switch(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        A naive kill-switch via netsh advfirewall.
        Blocks all outbound traffic except the VPN server IP.

        Args:
            server_ip (str): The VPN server IP.
        Returns:
            str: Success message.
        """
        try:
            logger.info(f"Enabling kill switch on Windows for {server_ip}...")

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
            res_block = subprocess.run(block_cmd, capture_output=True, text=True)
            if res_block.returncode != 0:
                raise RuntimeError(f"Failed to block all: {res_block.stdout or res_block.stderr}")

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
            res_allow = subprocess.run(allow_cmd, capture_output=True, text=True)
            if res_allow.returncode != 0:
                raise RuntimeError(
                    f"Failed to allow {server_ip}: {res_allow.stdout or res_allow.stderr}"
                )

            return "Kill switch enabled successfully."

        except Exception as exc:
            logger.error(f"Failed to enable kill switch: {exc}")
            raise exc

    def disable_kill_switch(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Remove kill-switch rules.

        Args:
            server_ip (str): The VPN server IP.

        Returns:
            str: Success message.
        """
        try:
            logger.info("Disabling kill switch on Windows.")

            remove_block = [
                "netsh",
                "advfirewall",
                "firewall",
                "delete",
                "rule",
                "name=KillSwitchBlockAll",
            ]
            res_block = subprocess.run(remove_block, capture_output=True, text=True)

            remove_allow = [
                "netsh",
                "advfirewall",
                "firewall",
                "delete",
                "rule",
                "name=KillSwitchAllowVPN",
            ]
            res_allow = subprocess.run(remove_allow, capture_output=True, text=True)

            return "Kill switch disabled successfully."
        except Exception as exc:
            logger.error(f"Failed to disable kill switch: {exc}")
            raise exc
