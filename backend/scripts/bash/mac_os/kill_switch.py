"""
Python script that contains a snippet of code for a kill switch feature in a VPN manager for macOS.

The script uses a bash script to enable and disable the kill switch. The script is used in the VPN manager to enable and disable the kill switch feature on macOS.
"""

import asyncio
import logging
import pathlib
from enum import Enum

logger = logging.getLogger(__name__)


class ScriptsNames(Enum):
    """
    Enum class for bash script names.
    """

    ENABLE_KILL_SWITCH = "enable_kill_switch.sh"
    DISABLE_KILL_SWITCH = "disable_kill_switch.sh"


SCRIPTS_DIR = pathlib.Path(__file__).parent.absolute()


async def enable_kill_switch() -> str:
    """
    Function to enable the kill switch using a bash script.
    """
    try:
        script_path = SCRIPTS_DIR / ScriptsNames.ENABLE_KILL_SWITCH.value

        proc = await asyncio.create_subprocess_exec(
            "bash", str(script_path), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"Failed to enable kill switch. Stderr: {stderr.decode()}")

        return stdout.decode()

    except Exception as exc:
        logger.error(f"Failed to enable kill switch: {exc}")
        raise exc


async def disable_kill_switch() -> str:
    """
    Function to disable the kill switch using a bash script.
    """
    try:
        script_path = SCRIPTS_DIR / ScriptsNames.DISABLE_KILL_SWITCH.value

        proc = await asyncio.create_subprocess_exec(
            "bash", str(script_path), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"Failed to disable kill switch. Stderr: {stderr.decode()}")

        return stdout.decode()

    except Exception as exc:
        logger.error(f"Failed to disable kill switch: {exc}")
        raise exc
