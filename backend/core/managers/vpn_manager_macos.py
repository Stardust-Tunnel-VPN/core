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
from scripts.bash.mac_os.kill_switch import ConfScriptsPaths
from utils.reusable.commands.macos.reusable_commands_map import cmds_map_macos

logger = logging.getLogger(__name__)


class MacOSL2TPConnector(IVpnConnector):
    """
    For macOS:
      - We can open System Settings -> Network to let user manually create an L2TP service.
      - If the user has already created a service named self.service_name (e.g. "MyL2TP"),
        we can connect/disconnect using `scutil --nc start/stop`.
         (Unfortunately, we can't establish it fully programmatically. Apple doesn't allow it.
         We can only create a connection manually in the System Settings -> Network pane
         and after that connect to it programmatically, that's the only way for 09.03.2025)

    METHODS THAT SHOULD BE IMPLEMENTED ACCORDING TO IVpnConnector:
    - connect ✅
    - disconnect ✅
    - status ✅
    - enable_kill_switch ✅ (not tested yet)
    - disable_kill_switch ✅ (not tested yet)
    """

    def __init__(
        self,
        service_name: str = "MyL2TP",
        service_psk_value: str = "vpn",
        current_vpn_ip: Optional[str] = None,
        _kill_switch_task: Optional[asyncio.Task] = None,
        _kill_switch_stop: bool = False,
    ):
        self.service_name = service_name
        self.service_psk_value = service_psk_value
        self.current_vpn_ip = current_vpn_ip
        self._kill_switch_task = _kill_switch_task
        self._kill_switch_stop = _kill_switch_stop

    async def connect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
        kill_switch_enabled: Optional[bool] = False,
    ) -> str:
        """
        VPN Class method to connect to a VPN server using L2TP/IPsec protocol on macOS.

        Raises:
            RuntimeError: If the connection fails.
        """
        if self.service_name is None:
            return "No service name provided for the VPN connection."

        try:
            # OPENING NETWORK SETTINGS
            logger.info("macOS: Opening Network Settings to let the user configure L2TP.")
            await open_macos_network_settings()

            # CONNECTION TO 'MYL2TP' SERVICE
            cmd = cmds_map_macos["connect_to_l2tp_service"] + [
                self.service_name,
                "--secret",
                self.service_psk_value,
            ]

            logger.info(f"Trying to start L2TP service '{self.service_name}' for IP={server_ip}")

            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err = stderr.decode().strip()
                msg = (
                    f"Failed to start VPN on macOS: {err}. "
                    "Make sure you've created the L2TP service in System Settings -> Network."
                )
                raise RuntimeError(msg)

            # EXTRACTING VPN IP ADDRESS (just for reference)
            self.current_vpn_ip = await extract_ip_address_from_service_name(self.service_name)

            # WAIT UP TO 10 SECONDS FOR ACTUAL "CONNECTED" STATUS
            connected = False
            for _ in range(10):
                st = await self.status()
                if st.lower() == "connected":
                    connected = True
                    break
                await asyncio.sleep(1)

            if not connected:
                raise RuntimeError(
                    "VPN did not become 'Connected' after 10s. Possibly failed to establish."
                )

            # If we reach here, VPN is "Connected"
            logger.info(f"Connected to {self.current_vpn_ip} via L2TP: {stdout.decode().strip()}")

            # If kill_switch_enabled=True, start background monitor
            if kill_switch_enabled:
                logger.info("Starting kill-switch monitor since kill_switch_enabled=True.")
                self.start_kill_switch_monitor(interval=2.0)

            return_str = f"Connected to {self.current_vpn_ip} via L2TP successfully!"
            return return_str

        except Exception as exc:
            logger.error(f"Failed to connect to {self.current_vpn_ip} on macOS: {exc}")
            raise exc

    async def disconnect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Class method to disconnect from a VPN server on macOS.

        Raises:
            RuntimeError: If the disconnection fails.
        """
        if not self.current_vpn_ip:
            return "No active VPN connection to disconnect from."

        try:
            # DISCONNECTING FROM 'MYL2TP' SERVICE
            cmd = cmds_map_macos["disconnect_from_l2tp_service"] + [self.service_name]

            logger.info(
                f"Stopping L2TP service '{self.service_name}' for IP={self.current_vpn_ip} with scutil."
            )

            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err = stderr.decode().strip()
                raise RuntimeError(f"Failed to stop VPN on macOS: {err}")

            logger.info(
                f"Disconnected VPN '{self.service_name}' from {self.current_vpn_ip}. "
                f"Output: {stdout.decode().strip()}"
            )

            return_str = (
                f"Disconnected VPN '{self.service_name}' from {self.current_vpn_ip} successfully!"
            )
            self.current_vpn_ip = None

            return return_str
        except Exception as exc:
            logger.error(f"Failed to disconnect from {self.service_name}: {exc}")
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
            # CHECKING STATUS OF 'MYL2TP' SERVICE
            cmd = cmds_map_macos["check_connection_status"] + [self.service_name]
            logger.info(f"Checking VPN status on macOS: {cmd}")

            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            output = stdout.decode().lower()

            if "disconnected" in output:
                return "Disconnected"
            elif "connected" in output:
                return "Connected"
            else:
                return "Unknown status"
        except Exception as exc:
            logger.error(f"Failed to check status on macOS: {exc}")
            return "Unknown status"

    async def enable_kill_switch(self) -> str:
        """
        Loads the kill switch configuration (blockall.conf) and enables PF firewall on macOS.

        Raises:
            RuntimeError: If the kill switch fails to enable.
        """
        try:
            cmd = ["sudo", "pfctl", "-f", ConfScriptsPaths.BLOCK_ALL_CONF.value, "-e"]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                raise RuntimeError(f"Failed to enable kill switch: {stderr.decode()}")

            return "Kill switch enabled (block all)."
        except Exception as exc:
            logger.error(f"Failed to enable kill switch on macOS: {exc}")
            raise exc

    async def disable_kill_switch(self) -> str:
        """
        Disables PF firewall on macOS. (It will allow all traffic)
        """
        try:
            cmd = ["sudo", "pfctl", "-d"]
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err = stderr.decode().strip()
                raise RuntimeError(f"Failed to disable kill switch: {err}")

            return "Kill switch disabled."
        except Exception as exc:
            logger.error(f"Failed to disable kill switch on macOS: {exc}")
            raise exc

    def start_kill_switch_monitor(self, interval: float = 0.3) -> None:
        """
        Enables a background task to monitor the kill-switch status.

        Args:
            interval (float): The interval in seconds to check the kill-switch status.

        Raises:
            Exception: If the task fails
        """
        try:
            self._kill_switch_stop = False
            loop = asyncio.get_event_loop()
            self._kill_switch_task = loop.create_task(self._kill_switch_loop(interval))
        except Exception as exc:
            logger.error(f"Failed to start kill-switch monitor: {exc}")
            raise exc

    async def stop_kill_switch_monitor(self) -> None:
        """
        Disables the background task that monitors the kill-switch status.
        """
        try:
            self._kill_switch_stop = True
            if self._kill_switch_task:
                await self._kill_switch_task
                self._kill_switch_task = None
        except Exception as exc:
            logger.error(f"Failed to stop kill-switch monitor: {exc}")
            raise exc

    async def _kill_switch_loop(self, interval: float) -> None:
        """
        Asynchronous loop to monitor the kill-switch status.

        - If status is 'Disconnected', we call enable_kill_switch()
        - If status is 'Connected', we call disable_kill_switch()
        """
        kill_switch_active = False
        logger.info("Kill-switch monitor started.")
        try:
            while not self._kill_switch_stop:
                st = await self.status()
                if st.lower() == "connected":
                    # VPN is up
                    if kill_switch_active:
                        logger.info("VPN reconnected -> disabling kill-switch.")
                        await self.disable_kill_switch()
                        kill_switch_active = False
                else:
                    # VPN is down
                    if not kill_switch_active:
                        logger.info("VPN disconnected -> enabling kill-switch.")
                        await self.enable_kill_switch()
                        kill_switch_active = True

                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("Kill-switch monitor cancelled.")
        except Exception as exc:
            logger.error(f"Kill-switch monitor crashed: {exc}")
        finally:
            logger.info("Kill-switch monitor stopped.")
