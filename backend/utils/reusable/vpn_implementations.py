from enum import Enum

"""
VPN Implementations Enum class for the VPN (based on L2TP/IPSec protocol for now)
"""


class VpnImplementation(str, Enum):
    """
    Describes the actual method used to connect L2TP/IPSec on each OS.
    - BUILT_IN_L2TP: Use built-in commands for Windows/macOS.
    - NMCLI_L2TP: Use NetworkManager-l2tp on Linux.
    - ALWAYS_ON_VPN: For Android, typically set in system settings.
    - ON_DEMAND_VPN: For iOS (MDM or OnDemand).
    """

    BUILT_IN_L2TP = "BUILT_IN_L2TP"
    NMCLI_L2TP = "NMCLI_L2TP"
    ALWAYS_ON_VPN = "ALWAYS_ON_VPN"
    ON_DEMAND_VPN = "ON_DEMAND_VPN"
