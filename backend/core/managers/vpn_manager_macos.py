# core/services/managers/vpn_manager_macos.py

"""
Python module for managing VPN connections on macOS.
"""

import asyncio
import logging
import traceback
from typing import Optional

from configuration.macos_l2tp_connection import (
    extract_ip_address_from_service_name, open_macos_network_settings)
from core.interfaces.ivpn_connector import IVpnConnector
from scripts.bash.mac_os.kill_switch import ConfScriptsPaths
from utils.reusable.commands.macos.commands_execution import run_macos_command
from utils.reusable.commands.macos.reusable_commands_map import cmds_map_macos

logger = logging.getLogger(__name__)


class MacOSL2TPConnector(IVpnConnector):
    """
    macOS L2TP Connector.

    For macOS:
      - Opens System Settings -> Network so the user can create the L2TP service manually.
      - Uses scutil commands to start/stop the service.
      - Uses pfctl to enable/disable the kill switch.

    METHODS IMPLEMENTED:
      - connect
      - disconnect
      - status
      - enable_kill_switch
      - disable_kill_switch
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
        Connects to a VPN server using L2TP/IPsec on macOS.

        Raises:
            RuntimeError: If connection fails.
        """
        if self.service_name is None:
            return "No service name provided for the VPN connection."

        try:
            logger.info("macOS: Opening Network Settings for L2TP configuration.")
            await open_macos_network_settings()

            # Build command to connect to the L2TP service.
            cmd = cmds_map_macos["connect_to_l2tp_service"] + [
                self.service_name,
                "--secret",
                self.service_psk_value,
            ]
            logger.info(
                f"Trying to start L2TP service '{self.service_name}' for IP={server_ip}"
            )

            stdout, _ = await run_macos_command(cmd, timeout=10)

            self.current_vpn_ip = await extract_ip_address_from_service_name(
                self.service_name
            )

            connected = False
            for _ in range(20):
                st = await self.status()
                if st.lower() == "connected":
                    connected = True
                    break
                await asyncio.sleep(1)

            if not connected:
                raise RuntimeError(
                    "VPN did not become 'Connected' after 20s. Possibly failed to establish."
                )

            logger.info(f"Connected to {self.current_vpn_ip} via L2TP: {stdout}")

            if kill_switch_enabled:
                logger.info("Starting kill-switch monitor (kill_switch_enabled=True).")
                self.start_kill_switch_monitor(interval=2.0)

            return f"Connected to {self.current_vpn_ip} via L2TP successfully!"

        except Exception as exc:
            logger.error(f"Failed to connect to {self.current_vpn_ip} on macOS: {exc}")
            raise

    async def disconnect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Disconnects from the VPN service on macOS.

        Raises:
            RuntimeError: If disconnection fails.
        """
        if not self.current_vpn_ip:
            return "No active VPN connection to disconnect from."

        try:
            cmd = cmds_map_macos["disconnect_from_l2tp_service"] + [self.service_name]
            logger.info(
                f"Stopping L2TP service '{self.service_name}' for IP={self.current_vpn_ip} using scutil."
            )

            stdout, _ = await run_macos_command(cmd, timeout=10)
            logger.info(
                f"Disconnected VPN '{self.service_name}' from {self.current_vpn_ip}. Output: {stdout}"
            )

            ret_str = f"Disconnected VPN '{self.service_name}' from {self.current_vpn_ip} successfully!"
            self.current_vpn_ip = None
            return ret_str
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
        Checks the VPN connection status on macOS.

        Returns:
            A string: "Connected", "Disconnected" or "Unknown status".
        """
        try:
            cmd = cmds_map_macos["check_connection_status"] + [self.service_name]
            logger.info(f"Checking VPN status on macOS: {cmd}")

            stdout, _ = await run_macos_command(cmd, timeout=5)
            output = stdout.lower()
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
        Enables the PF firewall kill switch using a block-all configuration.

        Raises:
            RuntimeError: If enabling the kill switch fails.
        """
        try:
            cmd = ["sudo", "pfctl", "-f", ConfScriptsPaths.BLOCK_ALL_CONF.value, "-e"]
            await run_macos_command(cmd, timeout=10)
            return "Kill switch enabled (block all)."
        except Exception as exc:
            logger.error(f"Failed to enable kill switch on macOS: {exc}")
            # Преобразуем сообщение, удаляя префикс "Command failed: " если он есть.
            err_msg = str(exc)
            if err_msg.startswith("Command failed: "):
                err_msg = err_msg[len("Command failed: ") :]
            raise RuntimeError(f"Failed to enable kill switch: {err_msg}")

    async def disable_kill_switch(self) -> str:
        """
        Disables the PF firewall on macOS (allows all traffic).

        Raises:
            RuntimeError: If disabling the kill switch fails.
        """
        try:
            cmd = ["sudo", "pfctl", "-d"]
            await run_macos_command(cmd, timeout=10)
            return "Kill switch disabled."
        except Exception as exc:
            logger.error(f"Failed to disable kill switch on macOS: {exc}")
            raise

    def start_kill_switch_monitor(self, interval: float = 0.3) -> None:
        """
        Starts a background task to monitor the kill switch status.
        """
        try:
            self._kill_switch_stop = False
            loop = asyncio.get_event_loop()
            self._kill_switch_task = loop.create_task(self._kill_switch_loop(interval))
        except Exception as exc:
            logger.error(f"Failed to start kill-switch monitor: {exc}")
            raise

    async def stop_kill_switch_monitor(self) -> None:
        """
        Stops the background kill switch monitoring task.
        """
        try:
            self._kill_switch_stop = True
            if self._kill_switch_task:
                await self._kill_switch_task
                self._kill_switch_task = None
        except Exception as exc:
            logger.error(f"Failed to stop kill-switch monitor: {exc}")
            raise

    async def _kill_switch_loop(self, interval: float) -> None:
        """
        Background loop to monitor kill switch status.

        - If VPN status is "Disconnected", enables kill switch.
        - If VPN status is "Connected", disables kill switch.
        """
        kill_switch_active = False
        logger.info("Kill-switch monitor started.")
        try:
            while not self._kill_switch_stop:
                st = await self.status()
                if st.lower() == "connected":
                    if kill_switch_active:
                        logger.info("VPN reconnected -> disabling kill switch.")
                        await self.disable_kill_switch()
                        kill_switch_active = False
                else:
                    if not kill_switch_active:
                        logger.info("VPN disconnected -> enabling kill switch.")
                        await self.enable_kill_switch()
                        kill_switch_active = True
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("Kill-switch monitor cancelled.")
        except Exception as exc:
            logger.error(f"Kill-switch monitor crashed: {exc}")
        finally:
            logger.info("Kill-switch monitor stopped.")
