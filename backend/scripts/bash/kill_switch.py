"""
Python script that contains a snippet of code for a kill switch feature in a VPN manager for macOS. The script is part of a larger project that manages VPN connections on macOS using L2TP/IPsec protocol. The script defines a class `MacOSL2TPConnector` that implements the `IVpnConnector` interface, which includes methods for connecting, disconnecting, checking status, enabling/disabling kill switch for VPN connections.
"""

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


def resolve_vpn_ip(vpn_server_ip: str) -> str:
    """
    Resolves a VPN server identifier to an IP address.
    If vpn_server_ip is already a valid IP, returns it unchanged.

    Args:
        vpn_server_ip (str): A hostname or IP.

    Returns:
        str: The resolved IP address.

    Raises:
        Exception: If hostname resolution fails.
    """
    try:
        ipaddress.ip_address(vpn_server_ip)

        return vpn_server_ip
    except ValueError:
        try:
            resolved_ip = socket.gethostbyname(vpn_server_ip)

            logger.info(f"Resolved hostname {vpn_server_ip} to IP {resolved_ip}")

            return resolved_ip
        except Exception as exc:
            logger.error(f"Failed to resolve hostname {vpn_server_ip}: {exc}")
            raise exc


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
    If vpn_server_ip is a hostname, it is resolved to an IP.

    Args:
        vpn_server_ip (str): The VPN server identifier.

    Returns:
        str: The formatted bash script.
    """
    if vpn_server_ip is None:
        raise ValueError("vpn_server_ip cannot be None")

    # Resolve hostname to IP if needed.
    resolved_ip = resolve_vpn_ip(vpn_server_ip)

    try:
        script = await read_script(ScriptsNames.ENABLE_KILL_SWITCH)
        # Replace placeholder with the actual VPN IP.
        return script.replace("{{VPN_SERVER_IP}}", resolved_ip)
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
