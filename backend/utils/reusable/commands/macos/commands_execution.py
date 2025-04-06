# core/backend/utils/reusable/commands/macos/commands_execution.py

import asyncio
import logging

logger = logging.getLogger(__name__)


async def run_macos_command(cmd: list, timeout: float = None) -> (str, str):
    """
    Executes a macOS command asynchronously and returns the decoded stdout and stderr.

    Args:
        cmd (list): List of command arguments (e.g. ["scutil", "--nc", "start", "MyL2TP"]).
        timeout (float, optional): Timeout in seconds.

    Returns:
        tuple: (stdout, stderr) as decoded strings.

    Raises:
        RuntimeError: If the command exits with a nonzero return code or times out.
    """
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        stdout_str = stdout.decode().strip()
        stderr_str = stderr.decode().strip()
        if process.returncode != 0:
            logger.error(f"Command {cmd} failed with error: {stderr_str}")
            raise RuntimeError(f"Command failed: {stderr_str}")
        return stdout_str, stderr_str
    except asyncio.TimeoutError:
        logger.error(f"Command {cmd} timed out after {timeout} seconds")
        raise RuntimeError("Command timed out")
