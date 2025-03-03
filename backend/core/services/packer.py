from core.services.parser import Parser
from utils.reusable.filters import filters_VPN_GATE

from typing import List, Dict


class Packer:
    """
    Python class that accepts a content from the parser class, filters it and returns the same CSV that has been filtered. (Based on the given filters)

    I created this class to filter the data from the vpngate.net website and return the data in a more readable format. I didn't remember any better name that potentially fits this class.

    CSV structure:
        HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,Uptime,TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64

    Filters:
        HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,Uptime,TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64
    """

    def __init__(self, content: str):
        self.content = content

    def transformContent(self) -> List[Dict[str, str]]:
        """
        Transforms the CSV-content from the parser class to a list of dictionaries.

        CSV-file structure:
            *vpn_servers
            headers (#HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,Uptime,TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64)
            content
            *
        """
        content = self.content.split("\n")
        headers = content[1].split(",")
        data = content[2:]

        # Transform the data
        transformed_data = []
        for row in data:
            row = row.split(",")
            transformed_row = {}
            for index, value in enumerate(row):
                if headers[index] in filters_VPN_GATE:
                    transformed_row[headers[index]] = value
            transformed_data.append(transformed_row)

        return transformed_data
