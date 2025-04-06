"""
Unit tests for MacOSL2TPConnector. This is different from
integration tests. Here we mostly mock out scutil/pfctl calls
and check behavior for success/failure/timeouts.
"""

import asyncio
import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.managers.vpn_manager_macos import MacOSL2TPConnector


@pytest.mark.asyncio
async def test_connect_ok():
    """
    Check that connect() doesn't raise if scutil returns 0
    and status eventually becomes 'Connected' within 10 tries.
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")

    # Mock scutil start success
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"", b"")

    with patch(
        "core.managers.vpn_manager_macos.extract_ip_address_from_service_name",
        return_value="1.2.3.4",
    ):
        result = await connector.connect(server_ip="1.1.1.1", kill_switch_enabled=False)
        assert "Connected to" in result
        assert connector.current_vpn_ip == "1.2.3.4"


@pytest.mark.asyncio
async def test_connect_scutil_fail():
    """
    If scutil returns non-zero, connect() should raise RuntimeError.
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")
    mock_proc = AsyncMock()
    mock_proc.returncode = 2
    mock_proc.communicate.return_value = (b"", b"scutil error")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(RuntimeError):
            await connector.connect()


@pytest.mark.asyncio
async def test_connect_status_timeout():
    """
    If after 30 tries we never see 'Connected', raise RuntimeError.
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"", b"")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with patch.object(connector, "status", return_value="Disconnected"):
            with pytest.raises(
                RuntimeError, match="VPN did not become 'Connected' after 30s."
            ):
                await connector.connect()


@pytest.mark.asyncio
async def test_disconnect_ok():
    """
    Check that disconnect returns expected string on success
    and sets current_vpn_ip to None.
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")
    connector.current_vpn_ip = "10.0.0.1"
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"Stopped", b"")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        result = await connector.disconnect()
        assert "Disconnected VPN 'MyL2TP' from 10.0.0.1" in result
        assert connector.current_vpn_ip is None


@pytest.mark.asyncio
async def test_disconnect_none():
    """
    If current_vpn_ip is None, method returns "No active VPN connection..."
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")
    connector.current_vpn_ip = None
    result = await connector.disconnect()
    assert result == "No active VPN connection to disconnect from."


@pytest.mark.asyncio
async def test_status_connected():
    """
    If scutil --nc status returns output containing 'connected',
    we parse it as 'Connected'.
    """
    connector = MacOSL2TPConnector(service_name="MyL2TP")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"Status: Connected", b"")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        st = await connector.status()
        assert st == "Connected"


@pytest.mark.asyncio
async def test_enable_kill_switch_ok():
    """
    If pfctl returns 0, we confirm success message.
    """
    connector = MacOSL2TPConnector()
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"Kill switch enabled", b"")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        out = await connector.enable_kill_switch()
        assert "Kill switch enabled" in out


@pytest.mark.asyncio
async def test_enable_kill_switch_fail():
    """
    If pfctl fails, we raise RuntimeError.
    """
    connector = MacOSL2TPConnector()

    with patch("subprocess.run") as mock_run:
        fake_completed = MagicMock()
        fake_completed.returncode = 1
        fake_completed.stderr = "pfctl error msg"
        fake_completed.stdout = ""
        mock_run.return_value = fake_completed

        with pytest.raises(
            RuntimeError,
            match=r"Failed to enable kill switch: Command.*pfctl error msg",
        ):
            await connector.enable_kill_switch()
