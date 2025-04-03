"""
Unit tests for configuration/macos_l2tp_connection.py
We have open_macos_network_settings, extract_ip_address_from_service_name, etc.

We will mock subprocess calls to avoid launching real commands.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from configuration.macos_l2tp_connection import (
    extract_ip_address_from_service_name,
    extract_ip_address_from_service_name_sync,
    open_macos_network_settings,
)


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
    If the subprocess fails, we expect an exception.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate.return_value = (b"", b"some error")
    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(Exception, match="Failed to open network settings:"):
            await open_macos_network_settings()


def test_extract_ip_address_from_service_name_sync_ok(monkeypatch):
    """
    We mock the synchronous subprocess.run to return a typical scutil --nc show output
    that includes lines like 'CommLocalAddress : 10.0.0.10' or 'CommRemoteAddress : 1.2.3.4'.
    """
    mock_run = MagicMock()
    mock_run.return_value.stdout = (
        "CommLocalAddress : 10.123.45.67\n" "CommRemoteAddress : 1.2.3.4\n"
    )
    mock_run.return_value.returncode = 0

    with patch("subprocess.run", mock_run):
        ip = extract_ip_address_from_service_name_sync("MyL2TP")
        # We expect local IP to be returned if found
        assert ip == "10.123.45.67"


def test_extract_ip_address_from_service_name_sync_no_local(monkeypatch):
    """
    If no local address is found, we fallback to remote if it's present.
    """
    mock_run = MagicMock()
    mock_run.return_value.stdout = "CommRemoteAddress : 9.9.9.9\n"
    mock_run.return_value.returncode = 0

    with patch("subprocess.run", mock_run):
        ip = extract_ip_address_from_service_name_sync("MyL2TP")
        assert ip == "9.9.9.9"


def test_extract_ip_address_from_service_name_sync_fail(monkeypatch):
    """
    If the subprocess raises or doesn't contain addresses, we get None.
    """
    mock_run = MagicMock(side_effect=Exception("some error"))
    with patch("subprocess.run", mock_run):
        ip = extract_ip_address_from_service_name_sync("FailVPN")
        assert ip is None


@pytest.mark.asyncio
async def test_extract_ip_address_from_service_name_ok():
    """
    The async version calls scutil with create_subprocess_exec. We mock that.
    Suppose it returns 'CommRemoteAddress : 2.2.2.2'
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
    If scutil returns a non-zero code, we raise a RuntimeError.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 2
    mock_proc.communicate.return_value = (b"", b"some scutil error")
    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(
            RuntimeError, match="Failed to extract IP address: some scutil error"
        ):
            await extract_ip_address_from_service_name("FailVPN")
