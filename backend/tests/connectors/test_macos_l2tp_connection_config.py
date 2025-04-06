"""
Unit tests for configuration/macos_l2tp_connection.py

This module contains unit tests for the macOS L2TP VPN connection configuration functions and methods.
The tests cover both synchronous and asynchronous functions, including:
- Opening macOS Network Settings.
- Extracting IP addresses from service names using `scutil`.
- Connecting to an L2TP VPN with optional kill switch functionality.

The tests use mocking to simulate subprocess calls and avoid executing real commands on the system.
This ensures the tests are isolated and do not depend on the actual system state or configuration.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from configuration.macos_l2tp_connection import (
    extract_ip_address_from_service_name,
    extract_ip_address_from_service_name_sync,
    open_macos_network_settings,
)
from core.managers.vpn_manager_macos import MacOSL2TPConnector


@pytest.mark.asyncio
async def test_open_macos_network_settings_ok():
    """
    If the subprocess returns code=0, we assume success.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"", b"")
    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        result = await open_macos_network_settings()
        assert "Opened macOS Network Settings successfully." in result


@pytest.mark.asyncio
async def test_open_macos_network_settings_fail():
    """
    Test the `open_macos_network_settings` function for a failure case.

    Simulates a subprocess call that returns a failure code (non-zero).
    Verifies that the function raises an exception with the appropriate error message.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate.return_value = (b"", b"some error")
    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(Exception, match="Failed to open network settings:"):
            await open_macos_network_settings()


def test_extract_ip_address_from_service_name_sync_ok(monkeypatch):
    """
    Test the synchronous `extract_ip_address_from_service_name_sync` function for a successful case.

    Simulates a subprocess call that returns typical `scutil --nc show` output containing
    both local and remote IP addresses. Verifies that the function extracts the local IP address.
    """
    mock_run = MagicMock()
    mock_run.return_value.stdout = (
        "CommLocalAddress : 10.123.45.67\n" "CommRemoteAddress : 1.2.3.4\n"
    )
    mock_run.return_value.returncode = 0

    with patch("subprocess.run", mock_run):
        ip = extract_ip_address_from_service_name_sync("MyL2TP")
        assert ip == "10.123.45.67"


def test_extract_ip_address_from_service_name_sync_no_local(monkeypatch):
    """
    Test the synchronous `extract_ip_address_from_service_name_sync` function when no local address is found.

    Simulates a subprocess call that returns `scutil --nc show` output containing only a remote IP address.
    Verifies that the function falls back to extracting the remote IP address.
    """
    mock_run = MagicMock()
    mock_run.return_value.stdout = "CommRemoteAddress : 9.9.9.9\n"
    mock_run.return_value.returncode = 0

    with patch("subprocess.run", mock_run):
        ip = extract_ip_address_from_service_name_sync("MyL2TP")
        assert ip == "9.9.9.9"


def test_extract_ip_address_from_service_name_sync_fail(monkeypatch):
    """
    Test the synchronous `extract_ip_address_from_service_name_sync` function for a failure case.

    Simulates a subprocess call that raises an exception or returns output without any IP addresses.
    Verifies that the function returns `None` in such cases.
    """
    mock_run = MagicMock(side_effect=Exception("some error"))
    with patch("subprocess.run", mock_run):
        ip = extract_ip_address_from_service_name_sync("FailVPN")
        assert ip is None


@pytest.mark.asyncio
async def test_extract_ip_address_from_service_name_ok():
    """
    Test the asynchronous `extract_ip_address_from_service_name` function for a successful case.

    Simulates a subprocess call that returns typical `scutil --nc show` output containing
    a remote IP address. Verifies that the function extracts the remote IP address.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"CommRemoteAddress : 2.2.2.2\n", b"")
    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        ip = await extract_ip_address_from_service_name("MyL2TP")
        assert ip == "2.2.2.2"


@pytest.mark.asyncio
async def test_extract_ip_address_from_service_name_error():
    """
    Test the asynchronous `extract_ip_address_from_service_name` function for a failure case.

    Simulates a subprocess call that returns a non-zero exit code and an error message.
    Verifies that the function raises a `RuntimeError` with the appropriate error message.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 2
    mock_proc.communicate.return_value = (b"", b"some scutil error")
    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(
            RuntimeError, match="Failed to extract IP address: some scutil error"
        ):
            await extract_ip_address_from_service_name("FailVPN")


@pytest.mark.asyncio
async def test_connect_with_kill_switch_sudo_fail():
    """
    Test the `connect` method of `MacOSL2TPConnector` when the kill switch is enabled
    and the sudo password verification fails.

    Simulates a failure in `_verify_sudo_password` and verifies that the method raises
    a `RuntimeError` before proceeding with the connection process.
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")

    with patch.object(
        connector, "_verify_sudo_password", side_effect=RuntimeError("Bad password")
    ):
        with patch.object(connector, "_check_sudo_password_stored") as mock_check:
            with pytest.raises(RuntimeError, match="Bad password"):
                await connector.connect(kill_switch_enabled=True)

            # mock_check.assert_called_once()


@pytest.mark.asyncio
async def test_connect_with_kill_switch_ok():
    """
    Test the `connect` method of `MacOSL2TPConnector` when the kill switch is enabled
    and the sudo password verification succeeds.

    Simulates successful calls to all required methods and verifies that the connection
    process completes successfully, returning a success message.
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")

    with patch.object(
        connector, "_verify_sudo_password", return_value=None
    ) as mock_verify:
        with patch(
            "core.managers.vpn_manager_macos.open_macos_network_settings",
            return_value=None,
        ):
            mock_run = AsyncMock()
            mock_run.return_value = (b"", b"")  # stdout, stderr
            with patch("core.managers.vpn_manager_macos.run_macos_command", mock_run):
                with patch(
                    "core.managers.vpn_manager_macos.extract_ip_address_from_service_name",
                    return_value="10.0.0.1",
                ):
                    with patch.object(connector, "status", return_value="Connected"):
                        result = await connector.connect(kill_switch_enabled=True)
                        assert "Connected to 10.0.0.1" in result

                        mock_verify.assert_called_once()


@pytest.mark.asyncio
async def test_connect_without_kill_switch_does_not_verify_sudo():
    """
    Test the `connect` method of `MacOSL2TPConnector` when the kill switch is disabled.

    Verifies that the `_verify_sudo_password` method is not called and the connection
    process completes successfully, returning a success message.
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")
    with patch.object(connector, "_verify_sudo_password") as mock_verify:
        with patch(
            "core.managers.vpn_manager_macos.open_macos_network_settings",
            return_value=None,
        ):
            mock_run = AsyncMock()
            mock_run.return_value = (b"", b"")
            with patch("core.managers.vpn_manager_macos.run_macos_command", mock_run):
                with patch(
                    "core.managers.vpn_manager_macos.extract_ip_address_from_service_name",
                    return_value="192.168.100.10",
                ):
                    with patch.object(connector, "status", return_value="Connected"):
                        result = await connector.connect(kill_switch_enabled=False)
                        assert "Connected to 192.168.100.10" in result

                        mock_verify.assert_not_called()
