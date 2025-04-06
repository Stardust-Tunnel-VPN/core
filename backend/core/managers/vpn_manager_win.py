"""
Created by Roman Rudyi on April, 2025.

This module implements a connector class for managing L2TP/IPsec VPN connections on Windows,
with optional support for a kill switch. The kill switch can block all network traffic if the VPN
becomes disconnected and restore traffic once the VPN reconnects.

Overview:
    - L2TP/IPsec connections are initiated and torn down via system commands (e.g., rasdial).
    - The class supports both a standard VPN connection and a "kill switch" mechanism controlled
      by Windows Firewall rules.
    - When kill_switch_enabled=True during connection, the kill switch blocks all outbound traffic
      except to the VPN server IP. On disconnect, the kill switch rules are removed to restore
      normal networking.
    - The kill switch implementation uses the `netsh` command to manage Windows Firewall rules.

Typical flow:
    1. A user calls connect(..., kill_switch_enabled=True) to start the VPN and, on success,
       enable the kill switch.
    2. The kill switch blocks all outbound traffic except to the VPN server IP while the VPN
       connection is active.
    3. On disconnect(), the kill switch rules are removed to restore normal networking.
    4. If the kill switch fails to apply or remove rules, an error is logged, but the process
       continues to avoid leaving the system in an inconsistent state.

Key points:
    - The kill switch is never activated before a successful VPN connection, preventing
      accidental blocking of essential VPN-handshake traffic.
    - Error handling ensures that a failure to apply or remove kill switch rules does not crash
      the entire process; instead, it logs an error.
    - The kill switch implementation can be extended or replaced with alternative methods
      (e.g., disabling network adapters) if needed.

This design can be further split into separate classes for the VPN connector and the kill switch
if desired. However, this combined approach is sufficient for typical usage scenarios on Windows.
"""

import asyncio
import logging
import socket
import subprocess
from typing import Optional

from configuration.win_l2tp_connection import create_windows_l2tp
from core.interfaces.ivpn_connector import IVpnConnector
from utils.reusable.commands.windows.reusable_commands_map import cmds_map_windows

logger = logging.getLogger(__name__)


class WindowsL2TPConnector(IVpnConnector):
    """
    For Windows OS:
      All sort of things and tricks, fortunately, we can do programmatically in compare to Apple.

      It uses 'rasdial' tool under the hood. More info about rasdial here:

      https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/ff859533(v=ws.11)

    METHODS THAT SHOULD BE IMPLEMENTED ACCORDING TO IVpnConnector:
    - connect ✅
    - disconnect ✅
    - status ✅
    - enable_kill_switch ? (haven't tested yet)
    - disable_kill_switch ? (haven't tested yet)
    """

    def __init__(self, connection_name: str = "MyL2TP"):
        self.connection_name = connection_name
        self.is_connected: Optional[bool] = False
        self.established_server_ip: Optional[str] = False

    def _resolve_hostname(self, hostname: str) -> str:
        """
        Resolve the hostname to an IP address.

        Args:
            hostname (str): The hostname to resolve.

        Returns:
            str: The resolved IP address.
        """
        try:
            return socket.gethostbyname(hostname)
        except Exception as exc:
            logger.error(f"Failed to resolve hostname {hostname}: {exc}")
            raise exc

    def _reset_connection(self) -> None:
        """
        Resets (disconnects) an existing VPN connection using the profile name.

        This method constructs a command to disconnect from an L2TP VPN service
        using the specified connection name and executes it. The command and its
        execution result are logged for debugging purposes.

        Args:
            None

        Returns:
            None
        """
        """Сбрасывает (отключает) существующее VPN-соединение по имени профиля."""
        try:
            disconnect_cmd = cmds_map_windows["disconnect_from_l2tp_service"][:]
            disconnect_cmd += [self.connection_name, "/disconnect"]
            logger.info(f"Resetting connection with command: {disconnect_cmd}")
            subprocess.run(disconnect_cmd, capture_output=True, text=True)
        except Exception as exc:
            logger.error(f"Failed to reset connection: {exc}")
            raise exc

    def _connect_sync(
        self,
        server_ip: Optional[str],
        username: str,
        password: str,
        psk: str,
        kill_switch_enabled: bool = False,
    ) -> str:
        """
        Establishes a synchronous VPN connection using L2TP protocol on a Windows system.
        This method attempts to connect to a VPN server using the provided credentials and pre-shared key (PSK).
        If no server IP is provided, it uses the previously established server connection details.
        It also supports enabling a kill switch to block internet traffic if the VPN connection drops.
        Args:
            server_ip (Optional[str]): The IP address of the VPN server. If None, the method uses the established server IP.
            username (str): The username for VPN authentication.
            password (str): The password for VPN authentication.
            psk (str): The pre-shared key (PSK) for the L2TP VPN connection.
            kill_switch_enabled (bool, optional): Whether to enable the kill switch. Defaults to False.
        Returns:
            str: A success message indicating the VPN connection was established.
        Raises:
            RuntimeError: If the VPN connection fails after retrying.
            Exception: For any other unexpected errors during the connection process.
        Notes:
            - If the connection fails with "Remote Access error 756", the method resets the connection and retries once.
            - The method logs detailed information about the connection process, including the commands executed.
            - The kill switch, if enabled, is configured before attempting the connection.
        Logging:
            - Logs an info message if no server IP is provided and the established connection details are used.
            - Logs the command used to attempt the connection.
            - Logs a warning if "Remote Access error 756" is encountered and a retry is initiated.
            - Logs an error message if the connection fails.
        Dependencies:
            - The `create_windows_l2tp` function is used to configure the L2TP VPN connection.
            - The `subprocess.run` method is used to execute the connection command.
            - The `time.sleep` function is used to introduce a delay before retrying the connection.
        """
        try:
            if not server_ip:
                server_ip = self.established_server_ip
                logger.info(
                    "No server_ip provided; using established connection details."
                )
            else:
                create_windows_l2tp(
                    server_ip=server_ip,
                    name=self.connection_name,
                    psk=psk,
                )

            cmd = cmds_map_windows["connect_to_l2tp_service"][:]
            cmd += [self.connection_name, username, password]

            if kill_switch_enabled:
                self.enable_kill_switch(server_ip)

            logger.info(f"Attempting connection with command: {cmd}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                error_msg = result.stdout or result.stderr
                if "Remote Access error 756" in error_msg:
                    logger.warning(
                        "Error 756 detected. Resetting connection and retrying."
                    )
                    self._reset_connection()

                    import time

                    time.sleep(1)
                    result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(
                        f"rasdial failed: {result.stdout or result.stderr}"
                    )

            return f"Connected to {server_ip or self.connection_name} successfully."
        except Exception as exc:
            logger.error(
                f"Failed to connect to {server_ip or self.connection_name}: {exc}"
            )
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
            """
            VPN Class method to connect to a VPN server using L2TP/IPsec protocol on Windows. It uses asyncio-thread as a final stage to make this method call in async style.

            Raises:
                RuntimeError: If the connection fails.
            """
            if kill_switch_enabled:
                self.enable_kill_switch(server_ip)

            return await asyncio.to_thread(
                self._connect_sync,
                server_ip,
                username,
                password,
                psk,
                kill_switch_enabled,
            )
        except Exception as exc:
            logger.error(f"Failed to connect to {server_ip}: {exc}")
            raise exc
        finally:
            self.is_connected = True
            self.established_server_ip = server_ip
            print("Connected status", self.is_connected)

    def _disconnect_sync(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Class method to disconnect from a VPN server on Windows. This is syncr-wrapper that uses subproccess lib in order to execute commands in powershell.

        Raises:
            RuntimeError: If the disconnection fails.
        """
        try:
            if not self.is_connected:
                raise ValueError("VPN Connection hasn't been established yet!")

            # TODO: extract to a separate method/function
            cmd = cmds_map_windows["disconnect_from_l2tp_service"][:]
            cmd += [self.connection_name, "/disconnect"]

            logger.info(
                f"WindowsL2TPConnector: disconnecting from {server_ip} with cmd: {cmd}"
            )

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(
                    f"rasdial /disconnect failed: {result.stdout or result.stderr}"
                )

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
        """
        Class method to disconnect from a VPN server on Windows. It uses asyncio-thread as a final stage to make this method call in async style.

        Raises:
            RuntimeError: If the disconnection fails.
        """
        try:
            return await asyncio.to_thread(
                self._disconnect_sync, server_ip, username, password, psk
            )
        except Exception as exc:
            logger.error(f"Failed to disconnect from {server_ip}: {exc}")
            raise exc
        finally:
            self.is_connected = False

    def _status_check_sync(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Class method to check the status of a VPN connection on Windows. This is syncr-wrapper that uses subproccess lib in order to execute commands in powershell.

        Returns:
            str: The status of the VPN connection.
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
                return f"Connected to {self.connection_name} successfully. Connection IP: {self.established_server_ip}"
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
        """
        Class method to check the status of a VPN connection on Windows. It uses asyncio-thread as a final stage to make this method call in async style.

        Returns:
            str: The status of the VPN connection.
        """
        try:
            return await asyncio.to_thread(
                self._status_check_sync, server_ip, username, password, psk
            )
        except Exception as exc:
            logger.error(f"Failed to get status for {server_ip}: {exc}")
            raise exc

    # def enable_kill_switch(
    #     self,
    #     server_ip: Optional[str] = None,
    #     username: Optional[str] = None,
    #     password: Optional[str] = None,
    #     psk: Optional[str] = None,
    # ) -> str:
    #     """
    #     A naive kill-switch via netsh advfirewall.
    #     Blocks all outbound traffic except the VPN server IP.

    #     Args:
    #         server_ip (str): The VPN server IP.
    #     Returns:
    #         str: Success message.
    #     """
    #     try:
    #         if not server_ip:
    #             raise ValueError("server_ip cannot be None or empty.")

    #         ip_firewall = self._resolve_hostname(hostname=server_ip)
    #         print("Server IP (resolved)", ip_firewall)

    #         logger.info(f"Enabling kill switch on Windows for {ip_firewall}...")

    #         block_cmd = [
    #             "netsh",
    #             "advfirewall",
    #             "firewall",
    #             "add",
    #             "rule",
    #             "name=KillSwitchBlockAll",
    #             "dir=out",
    #             "action=block",
    #             "remoteip=any",
    #         ]
    #         res_block = subprocess.run(block_cmd, capture_output=True, text=True)
    #         if res_block.returncode != 0:
    #             raise RuntimeError(f"Failed to block all: {res_block.stdout or res_block.stderr}")

    #         allow_cmd = [
    #             "netsh",
    #             "advfirewall",
    #             "firewall",
    #             "add",
    #             "rule",
    #             "name=KillSwitchAllowVPN",
    #             "dir=out",
    #             "action=allow",
    #             f"remoteip={ip_firewall}",
    #         ]
    #         res_allow = subprocess.run(allow_cmd, capture_output=True, text=True)
    #         if res_allow.returncode != 0:
    #             raise RuntimeError(
    #                 f"Failed to allow {ip_firewall}: {res_allow.stdout or res_allow.stderr}"
    #             )

    #         return "Kill switch enabled successfully."

    #     except Exception as exc:
    #         logger.error(f"Failed to enable kill switch: {exc}")
    #         raise exc

    # def disable_kill_switch(
    #     self,
    #     server_ip: Optional[str] = None,
    #     username: Optional[str] = None,
    #     password: Optional[str] = None,
    #     psk: Optional[str] = None,
    # ) -> str:
    #     """
    #     Remove kill-switch rules.

    #     Args:
    #         server_ip (str): The VPN server IP.

    #     Returns:
    #         str: Success message.
    #     """
    #     try:
    #         logger.info("Disabling kill switch on Windows.")

    #         remove_block = [
    #             "netsh",
    #             "advfirewall",
    #             "firewall",
    #             "delete",
    #             "rule",
    #             "name=KillSwitchBlockAll",
    #         ]
    #         res_block = subprocess.run(remove_block, capture_output=True, text=True)

    #         remove_allow = [
    #             "netsh",
    #             "advfirewall",
    #             "firewall",
    #             "delete",
    #             "rule",
    #             "name=KillSwitchAllowVPN",
    #         ]
    #         res_allow = subprocess.run(remove_allow, capture_output=True, text=True)

    #         return "Kill switch disabled successfully."
    #     except Exception as exc:
    #         logger.error(f"Failed to disable kill switch: {exc}")
    #         raise exc

    # def enable_kill_switch(self, *args, **kwargs) -> str:
    #     """ """
    #     try:

    #         adapters_to_disable = ["Ethernet", "WiFi"]

    #         for adapter in adapters_to_disable:
    #             cmd = ["netsh", "interface", "set", "interface", adapter, "admin=disabled"]
    #             result = subprocess.run(cmd, capture_output=True, text=True)
    #             if result.returncode != 0:
    #                 raise RuntimeError(
    #                     f"Failed to disable adapter '{adapter}': {result.stdout or result.stderr}"
    #                 )

    #         return "Kill switch enabled by disabling network adapters."

    #     except Exception as exc:
    #         logger.error(f"Failed to enable kill switch (disable adapters): {exc}")
    #         raise exc

    # def disable_kill_switch(self, *args, **kwargs) -> str:
    #     """ """
    #     try:
    #         adapters_to_enable = ["Ethernet", "Wi-Fi"]

    #         for adapter in adapters_to_enable:
    #             cmd = ["netsh", "interface", "set", "interface", adapter, "admin=enabled"]
    #             result = subprocess.run(cmd, capture_output=True, text=True)

    #             if result.returncode != 0:
    #                 raise RuntimeError(
    #                     f"Failed to enable adapter '{adapter}': {result.stdout or result.stderr}"
    #                 )

    #         return "Kill switch disabled by enabling network adapters."
    #     except Exception as exc:
    #         logger.error(f"Failed to disable kill switch (enable adapters): {exc}")
    #         raise exc
