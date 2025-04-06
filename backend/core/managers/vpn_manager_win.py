# core/services/managers/vpn_manager_win.py

import subprocess
import logging
import asyncio
import socket
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

    def _connect_sync(
        self,
        server_ip: str,
        username: str,
        password: str,
        psk: str,
        kill_switch_enabled: bool = False,
    ) -> str:
        """
        VPN Class method to connect to a VPN server using L2TP/IPsec protocol on Windows. This is syncr-wrapper that uses subproccess lib in order to execute commands in powershell.

        Raises:
            RuntimeError: If the connection fails.
        """
        try:
            if not server_ip:
                raise ValueError("server_ip cannot be None or empty.")

            create_windows_l2tp(
                server_ip=server_ip,
                name=self.connection_name,
                psk=psk,
                kill_switch_enabled=kill_switch_enabled,
            )

            # TODO: extract to a separate method/function
            cmd = cmds_map_windows["connect_to_l2tp_service"][:]
            final_username = username
            final_password = password
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
            """
            VPN Class method to connect to a VPN server using L2TP/IPsec protocol on Windows. It uses asyncio-thread as a final stage to make this method call in async style.

            Raises:
                RuntimeError: If the connection fails.
            """
            if kill_switch_enabled:
                self.enable_kill_switch(server_ip)

            return await asyncio.to_thread(
                self._connect_sync, server_ip, username, password, psk, kill_switch_enabled
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

            logger.info(f"WindowsL2TPConnector: disconnecting from {server_ip} with cmd: {cmd}")

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"rasdial /disconnect failed: {result.stdout or result.stderr}")

            return f"Disconnected from {server_ip} successfully."

        except Exception as exc:
            logger.error(f"Failed to disconnect from {server_ip}: {exc}")
            raise exc
        finally:
            return self.disable_kill_switch()

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
