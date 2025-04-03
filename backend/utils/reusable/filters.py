"""
Python module that contains the filters (as a custom type) that are used to filter the content from the parser class.
Should work with CSV data that we get from the VPNGATE.
Potentially can be used anywhere in the project.

Filters list:
    HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,Uptime,TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64

"""

filters_VPN_GATE = [
    "#HostName",
    "IP",
    "Score",
    "Ping",
    "Speed",
    "CountryLong",
    "CountryShort",
    "NumVpnSessions",
    "Uptime",
    "TotalUsers",
    "TotalTraffic",
    "LogType",
    "Operator",
    "Message",
    # "OpenVPN_ConfigData_Base64\r",
]

filters_VPN_GATE_set = set(filters_VPN_GATE)
