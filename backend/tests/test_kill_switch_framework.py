"""
Unit tests for the kill switch module:
  scripts/bash/mac_os/kill_switch.py

We have:
  - ScriptsNames Enum
  - ConfScriptsPaths Enum
  - enable_kill_switch / disable_kill_switch functions
These functions normally run real bash scripts. We can mock the subprocess call
to avoid actually running them, or we can test them for presence.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from scripts.bash.mac_os.kill_switch import (ConfScriptsPaths, ScriptsNames,
                                             disable_kill_switch,
                                             enable_kill_switch)


@pytest.mark.asyncio
async def test_enable_kill_switch_ok():
    """
    Tests enable_kill_switch() with a mocked subprocess call returning success.
    We expect no exception if returncode=0.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"Kill-switch enabled", b"")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        output = await enable_kill_switch()
        assert "Kill-switch enabled" in output


@pytest.mark.asyncio
async def test_enable_kill_switch_fail():
    """
    Tests enable_kill_switch() raising RuntimeError if script fails.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate.return_value = (b"", b"some error")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(RuntimeError, match="Failed to enable kill switch. Stderr: some error"):
            await enable_kill_switch()


@pytest.mark.asyncio
async def test_disable_kill_switch_ok():
    """
    Tests disable_kill_switch() success scenario.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = (b"Kill-switch disabled", b"")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        output = await disable_kill_switch()
        assert "Kill-switch disabled" in output


@pytest.mark.asyncio
async def test_disable_kill_switch_fail():
    """
    Tests disable_kill_switch() raising RuntimeError if script fails.
    """
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate.return_value = (b"", b"some disable error")

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(
            RuntimeError, match="Failed to disable kill switch. Stderr: some disable error"
        ):
            await disable_kill_switch()


def test_scripts_names_enum():
    """
    Test that ScriptsNames enum has the expected values.
    """
    assert ScriptsNames.ENABLE_KILL_SWITCH.value == "enable_kill_switch.sh"
    assert ScriptsNames.DISABLE_KILL_SWITCH.value == "disable_kill_switch.sh"


def test_conf_scripts_paths():
    """
    Test that ConfScriptsPaths enum references blockall.conf and passall.conf
    from the correct directory.
    We can't be sure those files exist, but we can check if the path is correct.
    """
    assert "blockall.conf" in ConfScriptsPaths.BLOCK_ALL_CONF.value
    assert "passall.conf" in ConfScriptsPaths.PASS_ALL_CONF.value
