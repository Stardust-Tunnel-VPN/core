"""
Python script that contains a snippet of code for a kill switch feature in a VPN manager for macOS. The script is part of a larger project that manages VPN connections on macOS using L2TP/IPsec protocol. The script defines a class `MacOSL2TPConnector` that implements the `IVpnConnector` interface, which includes methods for connecting, disconnecting, checking status, enabling/disabling kill switch for VPN connections.
"""

import asyncio
import logging
import pathlib
import ipaddress
import socket
from enum import Enum

import aiofiles

logger = logging.getLogger(__name__)


class ScriptsNames(Enum):
    """
    Enum class for bash script names.
    """

    ENABLE_KILL_SWITCH = "enable_kill_switch.sh"
    DISABLE_KILL_SWITCH = "disable_kill_switch.sh"


SCRIPTS_DIR = pathlib.Path(__file__).parent.absolute()


async def enable_kill_switch():
    script_path = SCRIPTS_DIR / ScriptsNames.ENABLE_KILL_SWITCH.value
    proc = await asyncio.create_subprocess_exec(
        "bash", str(script_path), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"Failed to enable kill switch. Stderr: {stderr.decode()}")
    return stdout.decode()


async def disable_kill_switch():
    script_path = SCRIPTS_DIR / ScriptsNames.DISABLE_KILL_SWITCH.value
    proc = await asyncio.create_subprocess_exec(
        "bash", str(script_path), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"Failed to disable kill switch. Stderr: {stderr.decode()}")
    return stdout.decode()


async def get_disable_kill_switch_script() -> str:
    """
    Asynchronously reads the disable kill switch script from file.

    Returns:
        str: The bash script content.
    """
    try:
        return await read_script(ScriptsNames.DISABLE_KILL_SWITCH)
    except Exception as exc:
        logger.error(f"Failed to get disable kill switch script: {exc}")
        raise exc
