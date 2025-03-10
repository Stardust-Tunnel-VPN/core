"""
Python script that contains a snippet of code for a kill switch feature in a VPN manager for macOS. The script is part of a larger project that manages VPN connections on macOS using L2TP/IPsec protocol. The script defines a class `MacOSL2TPConnector` that implements the `IVpnConnector` interface, which includes methods for connecting, disconnecting, checking status, enabling/disabling kill switch for VPN connections.
"""

import logging
import pathlib
from enum import Enum

import aiofiles

logger = logging.getLogger(__name__)


class ScriptsNames(Enum):
    """
    Enum class for bash script names.
    """

    ENABLE_KILL_SWITCH = "enable_kill_switch.sh"
    DISABLE_KILL_SWITCH = "disable_kill_switch.sh"


SCRIPTS_DIR = pathlib.Path(__file__).parent.absolute() / "bash"


async def read_script(script_name: ScriptsNames) -> str:
    """
    Asynchronously reads a bash script from the scripts directory.

    Args:
        script_name (ScriptsNames): The enum member with the script filename.

    Returns:
        str: The content of the script file.

    Raises:
        FileNotFoundError: If the script file does not exist.
    """
    script_path = SCRIPTS_DIR / script_name.value
    if not script_path.is_file():
        raise FileNotFoundError(f"Script not found: {script_path}")
    try:
        async with aiofiles.open(script_path, "r", encoding="utf-8") as f:
            return await f.read()
    except Exception as exc:
        logger.error(f"Failed to read script {script_name}: {exc}")
        raise exc


async def get_enable_kill_switch_script(vpn_server_ip: str) -> str:
    """
    Asynchronously reads and formats the enable kill switch script with the provided VPN server IP.

    Args:
        vpn_server_ip (str): The VPN server IP address.

    Returns:
        str: The formatted bash script.
    """
    try:
        script = await read_script(ScriptsNames.ENABLE_KILL_SWITCH)
        # Replace placeholder with the actual VPN IP.
        return script.replace("{{VPN_SERVER_IP}}", vpn_server_ip)
    except Exception as exc:
        logger.error(f"Failed to get enable kill switch script: {exc}")
        raise exc


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
