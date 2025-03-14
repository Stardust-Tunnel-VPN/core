# core/services/managers/vpn_manager_macos.py

"""
Python module for managing VPN connections on macOS.
"""

import asyncio
import logging
from typing import Optional

from configuration.macos_l2tp_connection import (
    extract_ip_address_from_service_name,
    open_macos_network_settings,
)
from core.interfaces.ivpn_connector import IVpnConnector
from scripts.bash.kill_switch import enable_kill_switch, disable_kill_switch
from utils.reusable.commands.macos.reusable_commands_map import cmds_map_macos

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

    def __init__(
        self,
        service_name: str = "MyL2TP",
        service_psk_value: str = "vpn",
        current_vpn_ip: Optional[str] = None,
    ):
        self.service_name = service_name
        self.service_psk_value = service_psk_value
        self.current_vpn_ip = current_vpn_ip

    # TODO: extract repeated vars to reusable-utils

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
        if self.service_name is not None:
            try:
                #### OPENING NETWORK SETTINGS ####
                logger.info("macOS: Opening Network Settings to let the user configure L2TP.")
                await open_macos_network_settings()

                #### CONNECTION TO 'MYL2TP' SERVICE ####
                cmd = cmds_map_macos["connect_to_l2tp_service"] + [
                    self.service_name,
                    "--secret",
                    self.service_psk_value,
                ]

                logger.info(
                    f"Trying to start L2TP service '{self.service_name}' for IP={server_ip}"
                )

                proc = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()

                #### EXTRACTING VPN IP ADDRESS ####
                self.current_vpn_ip = await extract_ip_address_from_service_name(self.service_name)

                if not self.current_vpn_ip:
                    raise RuntimeError(
                        "Failed to extract VPN IP address. Cannot enable kill switch."
                    )

                if proc.returncode != 0:
                    err = stderr.decode().strip()
                    msg = (
                        f"Failed to start VPN on macOS: {err}. "
                        "Make sure you've created the L2TP service in System Settings -> Network."
                    )
                    raise RuntimeError(msg)

                #### ENABLE KILL SWITCH (MACOS) ####
                if kill_switch_enabled:
                    logger.info("Enabling kill switch on macOS...")
                    logger.info(f"Current VPN IP: {self.current_vpn_ip}")

                    enable_script = await get_enable_kill_switch_script(self.current_vpn_ip)

                    proc = await asyncio.create_subprocess_shell(enable_script)
                    await proc.communicate()

                logger.info(
                    f"Connected to {self.current_vpn_ip} via L2TP: {stdout.decode().strip()}"
                )

                return_str = f"Connected to {self.current_vpn_ip} via L2TP successfully!"

                return return_str
            except Exception as exc:
                logger.error(f"Failed to connect to {self.current_vpn_ip} on macOS: {exc}")
                raise exc
        else:
            return "No service name provided for the VPN connection."

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
        if await self.status() == "Connected" and self.current_vpn_ip:
            try:
                # DISCONNECTING FROM 'MYL2TP' SERVICE #
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
                    f"Disconnected VPN '{self.service_name}' from {self.current_vpn_ip}. Output: {stdout.decode().strip()}"
                )

                return_str = f"Disconnected VPN '{self.service_name}' from {self.current_vpn_ip} successfully!"

                self.current_vpn_ip = None

                return return_str
            except Exception as exc:
                logger.error(f"Failed to disconnect from {self.service_name}: {exc}")
                raise
        else:
            return "No active VPN connection to disconnect from."

    # TODO: doesn't work
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
            cmd = cmds_map_macos["check_vpn_status"] + [self.service_name]

            logger.info(f"Checking VPN status on macOS: {cmd}")
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await proc.communicate()
            output = stdout.decode().lower()

            # TODO: extract to enum
            if "disconnected" in output:
                return "Disconnected"
            elif "connected" in output:
                return "Connected"
            else:
                return "Unknown status"
        except Exception as exc:
            logger.error(f"Failed to check status on macOS: {exc}")
            return "Unknown status"

    async def enable_kill_switch(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Class method to enable a kill switch on macOS.

        Raises:
            RuntimeError: If the kill switch fails to enable.
        """
        try:
            # ENABLE KILL SWITCH (MACOS)#
            if not self.current_vpn_ip:
                raise RuntimeError("VPN IP is missing. Connect to VPN before enabling kill switch.")

            logger.info(f"Enabling kill switch. Current VPN IP: {self.current_vpn_ip}")

            await enable_kill_switch()

            return f"Kill switch has been enabled successfully for {self.current_vpn_ip}!"
        except Exception as exc:
            logger.error(f"Failed to enable kill switch on macOS: {exc}")
            raise exc

    async def disable_kill_switch(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> Optional[str]:
        """
        Class method to disable a kill switch on macOS.

        Raises:
            RuntimeError: If the kill switch fails to disable.
        """
        try:
            # DISABLE KILL SWITCH (MACOS)#

            await disable_kill_switch()

            return f"Kill switch has been disabled successfully!"
        except Exception as exc:
            logger.error(f"Failed to disable kill switch on macOS: {exc}")
            raise exc
