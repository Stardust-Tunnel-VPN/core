# utils/reusable/commands/windows/reusable_commands_map.py

"""
Python module that stores the mapping of reusable terminal commands for VPN execution on Windows. (contains powershell, cmd, and other scripts that are used in the VPN manager for Windows; In array format)
"""

from typing import Dict, List

"""

Map of reusable terminal commands for VPN execution on Windows


"""

cmds_map_windows: Dict[str, List[str]] = {
    "create_windows_l2tp_connection": [
        "powershell",
        "-Command",
        r"""
    try {
        Import-Module RemoteAccess -ErrorAction SilentlyContinue

        Add-VpnConnection -Name '{name}' -ServerAddress '{server_ip}' -TunnelType L2TP -L2tpPsk '{psk}' `
            -AuthenticationMethod Pap,CHAP,MSCHAPv2 -AllUserConnection -Force -ErrorAction Stop

        Write-Host "Add-VpnConnection completed successfully."
    }
    catch {
        Write-Host ("Error: " + $_.Exception.Message)
        exit 1
    }
    """,
    ],
    "connect_to_l2tp_service": [
        "rasdial",
    ],
    "disconnect_from_l2tp_service": [
        "rasdial",
        "/DISCONNECT",
    ],
    "check_connection_status": [
        "rasdial",
    ],
}
