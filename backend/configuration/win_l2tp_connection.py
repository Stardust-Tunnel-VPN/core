import subprocess
import logging


def run_powershell_script(script: str) -> str:
    """
    Executes the given PowerShell script using subprocess.run.
    Raises RuntimeError if the script returns a non-zero exit code.

    Args:
        script (str): A multiline PowerShell script to be executed.

    Returns:
        str: The standard output text from the PowerShell execution.

    Raises:
        RuntimeError: If returncode != 0, indicating an error occurred.
    """
    cmd = ["powershell", "-Command", script]
    logging.debug(f"Running PowerShell command: {cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stdout or result.stderr or "Unknown PowerShell error.")
    return result.stdout or ""


def add_vpn_connection(server_ip: str, name: str, psk: str) -> str:
    """
    Calls Add-VpnConnection to create a new VPN profile.

    Args:
        server_ip (str): The IP address of the VPN server.
        name (str): The name of the VPN profile to create.
        psk (str): The pre-shared key for L2TP/IPSec.

    Returns:
        str: The output from the PowerShell script upon success.

    Raises:
        RuntimeError: If the PowerShell command fails.
    """
    script = f"""
    try {{
        Import-Module RemoteAccess -ErrorAction SilentlyContinue
        Add-VpnConnection -Name '{name}' -ServerAddress '{server_ip}' -TunnelType L2TP -L2tpPsk '{psk}' `
            -AuthenticationMethod Pap,CHAP,MSCHAPv2 -AllUserConnection -Force -ErrorAction Stop
        Write-Host "Add-VpnConnection completed successfully."
    }}
    catch {{
        Write-Host ("Error: " + $_.Exception.Message)
        exit 1
    }}
    """
    return run_powershell_script(script)


def set_vpn_connection(server_ip: str, name: str, psk: str) -> str:
    """
    Calls Set-VpnConnection to update an existing VPN profile.

    Args:
        server_ip (str): The new IP address for the existing VPN profile.
        name (str): The name of the VPN profile to update.
        psk (str): The new pre-shared key for L2TP/IPSec.

    Returns:
        str: The output from the PowerShell script upon success.

    Raises:
        RuntimeError: If the PowerShell command fails.
    """
    script = f"""
    try {{
        Import-Module RemoteAccess -ErrorAction SilentlyContinue
        Set-VpnConnection -Name '{name}' -ServerAddress '{server_ip}' -TunnelType L2TP -L2tpPsk '{psk}' `
            -AuthenticationMethod Pap,CHAP,MSCHAPv2 -AllUserConnection -Force -ErrorAction Stop
        Write-Host "Set-VpnConnection completed successfully."
    }}
    catch {{
        Write-Host ("Error: " + $_.Exception.Message)
        exit 1
    }}
    """
    return run_powershell_script(script)


def create_or_update_windows_l2tp(server_ip: str, name: str, psk: str) -> str:
    """
    Attempts to create or update a Windows L2TP VPN profile. Tries Add-VpnConnection first,
    and if it fails with an error indicating the profile already exists, calls Set-VpnConnection.

    Args:
        server_ip (str): The IP address of the VPN server.
        name (str): The VPN profile name.
        psk (str): The pre-shared key for L2TP/IPSec.

    Returns:
        str: The final output from either Add-VpnConnection or Set-VpnConnection.

    Raises:
        RuntimeError: If both creating and updating fail.
    """
    try:
        output = add_vpn_connection(server_ip, name, psk)
        logging.info("VPN profile created successfully.")
        return output
    except RuntimeError as add_err:
        err_text = str(add_err).lower()
        if "already been created" in err_text or "cannot create a file" in err_text:
            logging.warning(
                f"VPN profile '{name}' already exists. Attempting to update via Set-VpnConnection."
            )
            try:
                return set_vpn_connection(server_ip, name, psk)
            except RuntimeError as set_err:
                logging.error(f"Failed to update existing VPN profile '{name}': {set_err}")
                raise RuntimeError(f"Failed to update VPN profile '{name}': {set_err}") from set_err
        else:
            logging.error(f"Failed to add VPN profile '{name}': {add_err}")
            raise


def create_windows_l2tp(server_ip: str, name: str, psk: str = "vpn") -> str:
    """
    Entry point for creating or updating a Windows L2TP VPN connection.
    This function is typically called by the VPN connector code. If the named
    VPN profile does not exist, it will be created; if it already exists, its
    properties (such as the server IP) will be updated via Set-VpnConnection.

    Args:
        server_ip (str): The IP address of the VPN server.
        name (str): The VPN profile name.
        psk (str, optional): The L2TP/IPSec pre-shared key. Defaults to 'vpn'.

    Returns:
        str: The output from either Add-VpnConnection or Set-VpnConnection.

    Raises:
        RuntimeError: If creation or update fails.
    """
    logging.info(f"Ensuring L2TP VPN connection: name='{name}', server_ip='{server_ip}'")
    try:
        return create_or_update_windows_l2tp(server_ip, name, psk)
    except Exception as exc:
        logging.exception("Failed to create or update VPN connection")
        raise
