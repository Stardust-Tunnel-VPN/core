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
        "Add-VpnConnection -Name '{name}' -ServerAddress '{server_ip}' -TunnelType L2TP -L2tpPsk '{psk}' -AuthenticationMethod Pap,CHAP,MSCHAPv2 -AllUserConnection -Force",
    ],
    "connect_to_l2tp_service": [
        "rasdial",
        "{connection_name}",
        "{username}",
        "{password}",
    ],
    "disconnect_from_l2tp_service": [
        "rasdial",
        "{connection_name}",
        "/DISCONNECT",
    ],
    "check_connection_status": [
        "rasdial",
    ],
}
