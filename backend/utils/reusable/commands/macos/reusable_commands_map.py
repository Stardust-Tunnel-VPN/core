"""
Python module that stores the mapping of reusable terminal commands for VPN execution on macOS. (contains bash, python, and other scripts that are used in the VPN manager for macOS; In array format)
"""

from typing import Dict

# Map of reusable terminal commands for VPN execution on macOS

cmds_map: Dict[str, str] = {
    "open_macos_network_settings": [
        "open",
        "x-apple.systempreferences:com.apple.preferences.network",
    ],
    extract_ip_address_from_service_name: ["scutil", "--nc", "show", "<service_name>"],
    connect_to_l2tp_service: ["scutil", "--nc", "start", "<service_name>", "--secret", "<psk>"],
    disconnect_from_l2tp_service: ["scutil", "--nc", "stop", "<service_name>"],
    get_enable_kill_switch_script: ["enable_kill_switch.sh"],
    get_disable_kill_switch_script: ["disable_kill_switch.sh"],
    check_connection_status: ["scutil", "--nc", "status", "<service_name>"],
}
