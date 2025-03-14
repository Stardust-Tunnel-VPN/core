"""
Python module that stores the mapping of reusable terminal commands for VPN execution on macOS. (contains bash, python, and other scripts that are used in the VPN manager for macOS; In array format)
"""

from typing import Dict, List


"""
Map of reusable terminal commands for VPN execution on macOS

- open_macos_network_settings: Opens the macOS network settings.
- extract_ip_address_from_service_name: Extracts the IP address from a given service name.
- connect_to_l2tp_service: Connects to the L2TP service.
- disconnect_from_l2tp_service: Disconnects from the L2TP service.
- get_enable_kill_switch_script: Gets the script to enable the kill switch.
- get_disable_kill_switch_script: Gets the script to disable the kill switch.
- check_connection_status: Checks the connection status.

"""

cmds_map_macos: Dict[str, List[str]] = {
    "open_macos_network_settings": [
        "open",
        "x-apple.systempreferences:com.apple.preferences.network",
    ],
    "extract_ip_address_from_service_name": ["scutil", "--nc", "show"],
    "connect_to_l2tp_service": ["scutil", "--nc", "start"],
    "disconnect_from_l2tp_service": ["scutil", "--nc", "stop"],
    "get_enable_kill_switch_script": ["enable_kill_switch.sh"],
    "get_disable_kill_switch_script": ["disable_kill_switch.sh"],
    "check_connection_status": ["scutil", "--nc", "status"],
}
