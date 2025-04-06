"""
Created by Roman Rudyi on April, 2025.

This module implements a connector class for managing L2TP/IPsec VPN connections on macOS,
with an optional pfctl-based kill switch. The kill switch can automatically block all network
traffic if the VPN becomes disconnected, and restore traffic once the VPN reconnects.

Overview:
    - L2TP/IPsec connections are initiated and torn down via system commands (e.g., scutil).
    - The class supports both a standard VPN connection and a "kill switch" mechanism controlled
      by pf (Packet Filter).
    - When kill_switch_enabled=True during connection, a background monitor task continuously
      checks the VPN status. If the VPN goes 'Disconnected', the monitor invokes pfctl to
      block all network traffic; if the VPN returns to 'Connected', the monitor disables pfctl.
    - macOS Keychain integration allows seamless sudo operations for pfctl without prompting
      for a password each time. The SudoKeychainManager is used for reading/writing this
      password securely. If the password is absent or incorrect, pfctl commands will fail.

Typical flow:
    1. A user calls connect(..., kill_switch_enabled=True) to start the VPN and, on success,
       spawn the kill-switch monitor.
    2. The monitor loop enables pfctl if it detects a 'Disconnected' status, and disables it
       when the VPN transitions back to 'Connected'.
    3. On disconnect(), the kill-switch monitor is stopped and pfctl is disabled to restore
       normal networking.
    4. If Keychain password checks fail or the user lacks sudo privileges for pfctl, any
       attempt to enable/disable pf results in an error.

Key points:
    - The kill switch is never activated before a successful VPN connection, preventing
      accidental blocking of essential VPN-handshake traffic.
    - The stored sudo password is verified by a simple check command (e.g., 'sudo whoami') to
      confirm correctness before kill-switch usage.
    - If pfctl does not require a password (e.g., NOPASSWD in /etc/sudoers), Keychain storage
      may be unnecessary.
    - Error handling ensures that a failure to apply pfctl operations does not crash the
      entire process; instead, it logs an error. If needed, the kill-switch monitor can be
      stopped on error.

This design can be further split into separate classes for the VPN connector, pfctl kill switch,
and the kill-switch monitor if desired (see the note in MacOSL2TPConnector). However, this
combined approach is sufficient for typical usage scenarios.
"""

import asyncio
import logging
import subprocess
from typing import Optional

from configuration.macos_l2tp_connection import (
    extract_ip_address_from_service_name,
    open_macos_network_settings,
)
from core.interfaces.ivpn_connector import IVpnConnector
from core.managers.keychain_manager_macos import SudoKeychainManager
from scripts.bash.mac.kill_switch import ConfScriptsPaths
from utils.reusable.commands.macos.commands_execution import run_macos_command
from utils.reusable.commands.macos.reusable_commands_map import cmds_map_macos

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------------------
# macOS L2TP Connector with optional pfctl kill switch
# ------------------------------------------------------------------------------------------


class MacOSL2TPConnector(IVpnConnector):
    """
    Handles macOS L2TP/IPsec VPN connections and an optional pfctl-based kill switch.

    Kill-switch behavior:
      - The switch is never enabled before VPN is successfully connected.
      - If kill_switch_enabled=True, a background task is created upon connection to monitor
        VPN status. When the VPN becomes disconnected, pfctl is enabled to block all traffic.
        When the VPN reconnects, pfctl is disabled to restore normal traffic.

    Sudo password is obtained from the macOS Keychain via SudoKeychainManager. If no valid
    password is saved, pfctl commands will fail. You can verify correctness of the password
    by an internal check prior to enabling the kill switch.

    Note: In some scenarios, macOS or sudo configuration may not require a password for pfctl
    (e.g., NOPASSWD in /etc/sudoers). In such cases, the Keychain storage is unused.
    """

    def __init__(
        self,
        service_name: str = "MyL2TP",
        service_psk_value: str = "vpn",
        current_vpn_ip: Optional[str] = None,
        _kill_switch_task: Optional[asyncio.Task] = None,
        _kill_switch_stop: bool = False,
        keychain_manager: Optional[SudoKeychainManager] = None,
    ):
        """
        Initializes the MacOSL2TPConnector.

        :param service_name: Name of the L2TP service (as configured in macOS Network settings).
        :param service_psk_value: The IPSec pre-shared key (PSK) for L2TP.
        :param current_vpn_ip: Stores the VPN IP address once connected, if known.
        :param _kill_switch_task: Reference to the background asyncio Task monitoring kill-switch.
        :param _kill_switch_stop: A boolean flag indicating the kill-switch monitor should stop.
        :param keychain_manager: A SudoKeychainManager for retrieving/storing the sudo password
                                 in the Keychain. Defaults to a new instance if not provided.
        """
        self.service_name = service_name
        self.service_psk_value = service_psk_value
        self.current_vpn_ip = current_vpn_ip
        self._kill_switch_task = _kill_switch_task
        self._kill_switch_stop = _kill_switch_stop
        self.keychain_manager = keychain_manager or SudoKeychainManager()

    # ------------------------------------------------------------------------------------------
    # Utilities: password checks and synchronous sudo calls
    # ------------------------------------------------------------------------------------------

    def _check_sudo_password_stored(self) -> None:
        """
        Ensures a sudo password is present in the Keychain.

        :raises ValueError: If the password is absent or empty in the Keychain.
        """
        pw = self.keychain_manager.get_sudo_password()
        if not pw or pw == "":
            raise ValueError("No sudo password found in Keychain or access denied.")

    def _verify_sudo_password(self) -> None:
        """
        Validates that the stored sudo password can actually authenticate.

        :raises RuntimeError: If the password is invalid for sudo operations.
        """
        pw = self.keychain_manager.get_sudo_password()
        if not pw:
            raise RuntimeError("No sudo password found in Keychain.")

        proc = subprocess.run(
            ["sudo", "-S", "whoami"], input=pw + "\n", text=True, capture_output=True
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"Sudo password verification failed (code {proc.returncode}): {proc.stderr}"
            )

    def _run_sudo_with_stored_password(self, command: list[str]) -> str:
        """
        Executes the given command via 'sudo -S' using the password from Keychain.

        :param command: Command arguments excluding 'sudo' itself.
        :return: The command's stdout, or an empty string if there was no output.
        :raises RuntimeError: If the sudo command exits with a non-zero code or
                              if the stored password is not available.
        """
        pw = self.keychain_manager.get_sudo_password()
        if not pw:
            raise RuntimeError(
                "No sudo password found in Keychain or access was denied."
            )

        full_cmd = ["sudo", "-S"] + command
        proc = subprocess.run(full_cmd, input=pw + "\n", text=True, capture_output=True)

        if proc.returncode != 0:
            raise RuntimeError(
                f"Command '{' '.join(full_cmd)}' failed (code {proc.returncode}): {proc.stderr}"
            )
        return proc.stdout or ""

    # ------------------------------------------------------------------------------------------
    # VPN Connection Methods
    # ------------------------------------------------------------------------------------------

    async def status(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Checks the L2TP connection status (Connected, Disconnected, or Unknown).

        :return: "Connected", "Disconnected", or "Unknown status".
        """
        try:
            cmd = cmds_map_macos["check_connection_status"] + [self.service_name]
            stdout, _ = await run_macos_command(cmd, timeout=5)
            lower_out = stdout.lower()
            if "disconnected" in lower_out:
                return "Disconnected"
            elif "connected" in lower_out:
                return "Connected"
            else:
                return "Unknown status"
        except Exception as exc:
            logger.error(f"Failed to check status on macOS: {exc}")
            return "Unknown status"

    async def _wait_for_connection(self, timeout: int = 30) -> bool:
        """
        Polls the VPN status until it's 'Connected' or the timeout expires.

        :param timeout: Maximum number of seconds to wait.
        :return: True if VPN is connected within the timeframe, False otherwise.
        """
        for _ in range(timeout):
            st = await self.status()
            if st.lower() == "connected":
                return True
            await asyncio.sleep(1)
        return False

    async def _connect_with_kill_switch(
        self,
        server_ip: Optional[str],
        username: Optional[str],
        password: Optional[str],
        psk: Optional[str],
    ) -> str:
        """
        Connects to L2TP/IPsec and, upon success, starts the kill-switch monitor.

        :raises ValueError: If there's no password in Keychain.
        :raises RuntimeError: If VPN fails to connect or sudo password is invalid.
        """
        try:
            self._verify_sudo_password()
            self._check_sudo_password_stored()

            await open_macos_network_settings()
            cmd = cmds_map_macos["connect_to_l2tp_service"] + [
                self.service_name,
                "--secret",
                self.service_psk_value,
            ]
            _, _ = await run_macos_command(cmd, timeout=10)

            self.current_vpn_ip = await extract_ip_address_from_service_name(
                self.service_name
            )
            connected = await self._wait_for_connection(timeout=90)
            if not connected:
                raise RuntimeError("VPN did not become 'Connected' after 90s.")

            self.start_kill_switch_monitor(interval=2.0)
            return f"Connected to {self.current_vpn_ip} (kill-switch monitor active)."
        except (ValueError, RuntimeError) as exc:
            logger.error(f"Cannot enable kill-switch: {exc}")
            raise

    async def _connect_without_kill_switch(
        self,
        server_ip: Optional[str],
        username: Optional[str],
        password: Optional[str],
        psk: Optional[str],
    ) -> str:
        """
        Connects to L2TP/IPsec without enabling the kill-switch monitor.
        """
        try:
            await open_macos_network_settings()
            cmd = cmds_map_macos["connect_to_l2tp_service"] + [
                self.service_name,
                "--secret",
                self.service_psk_value,
            ]
            _, _ = await run_macos_command(cmd, timeout=10)

            self.current_vpn_ip = await extract_ip_address_from_service_name(
                self.service_name
            )
            connected = await self._wait_for_connection(timeout=30)
            if not connected:
                raise RuntimeError("VPN did not become 'Connected' after 30s.")

            return f"Connected to {self.current_vpn_ip} (no kill-switch)."
        except Exception as exc:
            logger.error(f"Failed to connect without kill-switch on macOS: {exc}")
            raise

    async def connect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
        kill_switch_enabled: bool = False,
    ) -> str:
        """
        Public method to connect to the VPN. If kill_switch_enabled=True, the kill-switch
        monitor is launched after successful connection.

        :return: A string describing the result ("Connected..." or an error).
        :raises RuntimeError: If the connection fails or kill-switch cannot be activated.
        """
        if not self.service_name:
            return "No service name provided."
        try:
            if kill_switch_enabled:
                return await self._connect_with_kill_switch(
                    server_ip, username, password, psk
                )
            else:
                return await self._connect_without_kill_switch(
                    server_ip, username, password, psk
                )
        except Exception as exc:
            logger.error(f"Failed to connect on macOS: {exc}")
            raise

    async def disconnect(
        self,
        server_ip: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        psk: Optional[str] = None,
    ) -> str:
        """
        Disconnects from the current L2TP VPN (if any). Also stops the kill-switch monitor
        and attempts to disable the kill-switch.

        :return: A string describing the disconnection result.
        :raises RuntimeError: If any error occurs during disconnection or kill-switch teardown.
        """
        if not self.current_vpn_ip:
            return "No active VPN connection to disconnect from."

        try:
            cmd = cmds_map_macos["disconnect_from_l2tp_service"] + [self.service_name]
            _, _ = await run_macos_command(cmd, timeout=10)
            result = f"Disconnected VPN '{self.service_name}' from {self.current_vpn_ip} successfully!"
            logger.info(result)
            self.current_vpn_ip = None
            return result
        except Exception as exc:
            logger.error(f"Failed to disconnect from {self.service_name}: {exc}")
            raise
        finally:
            try:
                await self.stop_kill_switch_monitor()
            except Exception as e:
                logger.error(f"Error stopping kill switch monitor: {e}")
            try:
                await self.disable_kill_switch()
            except Exception as e:
                logger.error(f"Error disabling kill switch: {e}")

    # ------------------------------------------------------------------------------------------
    # Synchronous pfctl methods for enabling/disabling kill switch
    # ------------------------------------------------------------------------------------------

    def _enable_kill_switch_sync(self) -> str:
        """
        Enables pf-based kill switch synchronously via pfctl -f <blockall.conf> -e.

        :return: The output from pfctl command.
        :raises RuntimeError: If the pfctl command fails.
        """
        cmd = ["/sbin/pfctl", "-f", ConfScriptsPaths.BLOCK_ALL_CONF.value, "-e"]
        return self._run_sudo_with_stored_password(cmd)

    def _disable_kill_switch_sync(self) -> str:
        """
        Disables pf-based kill switch synchronously via pfctl -d.

        :return: The output from pfctl command.
        :raises RuntimeError: If the pfctl command fails.
        """
        cmd = ["pfctl", "-d"]
        return self._run_sudo_with_stored_password(cmd)

    # ------------------------------------------------------------------------------------------
    # Asynchronous wrappers for kill switch operations
    # ------------------------------------------------------------------------------------------

    async def enable_kill_switch(self) -> str:
        """
        Enables the pf-based kill switch asynchronously.

        :return: A status string describing the pfctl output.
        :raises RuntimeError: If enabling pfctl fails or password is invalid.
        """
        try:
            loop = asyncio.get_running_loop()
            output = await loop.run_in_executor(None, self._enable_kill_switch_sync)
            logger.info("Kill switch enabled (block all).")
            return output or "Kill switch enabled (block all)."
        except Exception as exc:
            logger.error(f"Failed to enable kill switch: {exc}")
            raise RuntimeError(f"Failed to enable kill switch: {exc}")

    async def disable_kill_switch(self) -> str:
        """
        Disables the pf-based kill switch asynchronously.

        :return: A status string describing the pfctl output.
        :raises RuntimeError: If disabling pfctl fails or password is invalid.
        """
        try:
            loop = asyncio.get_running_loop()
            output = await loop.run_in_executor(None, self._disable_kill_switch_sync)
            logger.info("Kill switch disabled.")
            return output or "Kill switch disabled."
        except Exception as exc:
            logger.error(f"Failed to disable kill switch: {exc}")
            raise RuntimeError(f"Failed to disable kill switch: {exc}")

    # ------------------------------------------------------------------------------------------
    # Kill-switch monitor (background task)
    # ------------------------------------------------------------------------------------------

    def start_kill_switch_monitor(self, interval: float = 0.3) -> None:
        """
        Spawns a background task that periodically checks the VPN status. When 'Disconnected',
        it calls enable_kill_switch(). When 'Connected', it calls disable_kill_switch().

        :param interval: Seconds to wait between checks.
        :raises RuntimeError: If creation of the async task fails.
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
        Stops the background kill-switch monitor, if running.
        Does not automatically disable pfctl.

        :raises RuntimeError: If any error occurs when stopping the task.
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
        Core loop of the kill-switch monitor task.
        Checks VPN status, enabling pfctl if disconnected and disabling it if reconnected.

        :param interval: Seconds to wait between checks.
        """
        kill_switch_active = False
        logger.info("Kill-switch monitor started.")
        try:
            while not self._kill_switch_stop:
                st = await self.status()
                if st.lower() == "connected":
                    if kill_switch_active:
                        logger.info("VPN reconnected -> disabling kill switch.")
                        try:
                            await self.disable_kill_switch()
                        except Exception as e:
                            logger.error(f"Error disabling kill switch: {e}")
                        kill_switch_active = False
                else:
                    if not kill_switch_active:
                        logger.info("VPN disconnected -> enabling kill switch.")
                        try:
                            await self.enable_kill_switch()
                            kill_switch_active = True
                        except Exception as e:
                            logger.error(f"Error enabling kill switch: {e}")
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info("Kill-switch monitor cancelled.")
        except Exception as exc:
            logger.error(f"Kill-switch monitor crashed: {exc}")
        finally:
            logger.info("Kill-switch monitor stopped.")
