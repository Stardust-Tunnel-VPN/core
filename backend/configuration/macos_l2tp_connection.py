# configuration/macos_l2tp_connection.py

import asyncio
import logging
import subprocess
from typing import Optional

from utils.reusable.commands.macos.reusable_commands_map import cmds_map_macos

logger = logging.getLogger(__name__)

"""
Python configuration snippet for creating a new L2TP VPN connection on macOS. 
Unfortunately, Apple restricts the ability to create VPN connections programmatically...
"""


async def open_macos_network_settings() -> str:
    try:
        cmd = cmds_map_macos["open_macos_network_settings"]

        logger.info(f"Opening macOS Network Settings with command: {' '.join(cmd)}")

        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.communicate()

        logger.info("Instruct the user to create / configure a VPN (L2TP/IPsec) service manually.")
        return "Opened macOS Network Settings successfully."

    except Exception as exc:
        logger.error(f"Failed to open network settings: {exc}")
        raise


def extract_ip_address_from_service_name_sync(service_name: str) -> Optional[str]:
    """
    Synchronously extracts the VPN IP address by running 'scutil --nc show <service_name>'.
    Tries to extract the local IP address first; if not found, returns the remote address.

    Args:
        service_name (str): The name of the VPN service.

    Returns:
        Optional[str]: The local VPN IP address if available, otherwise the remote address, or None if not found.
    """
    try:
        result = subprocess.run(
            cmds_map_macos["extract_ip_address_from_service_name"] + [service_name],
            capture_output=True,
            text=True,
            check=True,
        )

        local_ip = None
        remote_ip = None

        for line in result.stdout.splitlines():
            lower_line = line.lower()
            if "commlocaladdress" in lower_line:
                parts = line.split(":")
                if len(parts) > 1:
                    local_ip = parts[1].strip()
            elif "commremoteaddress" in lower_line:
                parts = line.split(":")
                if len(parts) > 1:
                    remote_ip = parts[1].strip()

        return local_ip if local_ip else remote_ip
    except Exception as exc:
        logger.error(f"Error in extract_ip_address_from_service_name_sync: {exc}")
    return None


# async def wait_for_vpn_ip_sync(
#     service_name: str = "MyL2TP", retries: int = 5, delay: float = 5.0
# ) -> str:
#     """
#     Awaits a valid VPN IP address by calling the synchronous extraction function
#     in a separate thread.

#     Args:
#         service_name (str): The name of the VPN service.
#         retries (int): Maximum number of retries.
#         delay (float): Delay between retries in seconds.

#     Returns:
#         str: The extracted VPN IP address.

#     Raises:
#         RuntimeError: If a valid IP is not obtained after the retries.
#     """
#     try:
#         for attempt in range(retries):
#             vpn_ip = await asyncio.to_thread(
#                 extract_ip_address_from_service_name_sync, service_name
#             )
#             if vpn_ip:
#                 return vpn_ip
#             await asyncio.sleep(delay)
#         raise RuntimeError("Failed to extract VPN IP address after multiple retries.")
#     except Exception as exc:
#         logger.error(f"Error in wait_for_vpn_ip_sync: {exc}")
#         raise exc


async def extract_ip_address_from_service_name(service_name: str) -> str:
    """
    Extracts the IP address from the given macOS service name.
    :param service_name: The macOS service name to extract the IP address from.
    :returns: The IP address extracted from the service name.
    """
    try:

        logger.info(f"Extracting IP address from macOS service name: {service_name}")

        proc = await asyncio.create_subprocess_exec(
            *cmds_map_macos["extract_ip_address_from_service_name"] + [service_name],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        for line in stdout.decode().splitlines():
            if "commremoteaddress" in line.lower():
                return line.split(":")[-1].strip()

        if proc.returncode != 0:
            raise RuntimeError(f"Failed to extract IP address: {stderr.decode()}")

    except Exception as exc:
        logger.error(f"Failed to extract IP address from service name: {exc}")
        raise exc
