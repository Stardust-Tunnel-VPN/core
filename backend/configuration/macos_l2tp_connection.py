# configuration/macos_l2tp_connection.py

import asyncio
import logging

logger = logging.getLogger(__name__)

"""
Python configuration snippet for creating a new L2TP VPN connection on macOS. 
Unfortunately, Apple restricts the ability to create VPN connections programmatically...
"""


async def open_macos_network_settings() -> None:
    """
    Opens the macOS System Settings -> Network pane (on Ventura+) or
    System Preferences -> Network (on older macOS).
    Real behavior may vary by macOS version.
    """
    try:
        cmd = ["open", "x-apple.systempreferences:com.apple.preferences.network"]
        logger.info(f"Opening macOS Network Settings: {cmd}")
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.communicate()
        logger.info("Instruct the user to create / configure a VPN (L2TP/IPsec) service manually.")
    except Exception as exc:
        logger.error(f"Failed to open network settings: {exc}")
        raise
