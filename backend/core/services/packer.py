from typing import List, Dict
from utils.reusable.filters import filters_VPN_GATE
import traceback
from pprint import pformat


class Packer:
    """
    A class that accepts CSV content from the parser, filters it based on the provided filters,
    and returns the filtered CSV data as a list of dictionaries.

    CSV structure:
      HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,
      Uptime,TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64

    Filters:
      HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,
      Uptime,TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64
    """

    def __init__(self, content: str):
        self.content = content

    def transformContent(self) -> List[Dict[str, str]]:
        """
        Transforms the CSV content into a list of dictionaries, keeping only the allowed fields.

        Returns:
            A list of dictionaries representing the filtered CSV rows.
            Returns an empty list if an error occurs.
        """
        try:
            # TODO: separate this code to functions, try to make it more human-readable as well...
            csv_lines = self.content.split("\n")
            if len(csv_lines) < 2:
                return []

            header_line = csv_lines[1]
            headers = header_line.split(",")

            allowed_fields = set(filters_VPN_GATE)

            allowed_indices = [
                index for index, header in enumerate(headers) if header in allowed_fields
            ]

            allowed_header_names = [headers[i] for i in allowed_indices]

            transformed_data: List[Dict[str, str]] = []

            for line in csv_lines[2:]:
                if not line.strip():
                    continue  # Skip empty lines
                row_values = line.split(",")
                row_dict = {}
                for allowed_index, header_name in zip(allowed_indices, allowed_header_names):
                    # if the iterated row ([value1, value2, valueN, ...]) has more values ​​than the iteration index (this means that the subsequent index value goes beyond the values ​​of this row, i.e. there must be a situation where allowed_index must BE INCLUDED in the number of row values ​​(len(row_values)), otherwise during iteration it will simply go beyond the indices and assign something incorrectly)
                    if allowed_index < len(row_values):
                        row_dict[header_name] = row_values[allowed_index]
                transformed_data.append(row_dict)

            return self.formatTransformedContent(transformed_data)

        except Exception as e:
            print("Error in transformContent:", str(e))
            traceback.print_exc()
            return []

    def formatTransformedContent(self, data: List[Dict[str, str]]) -> str:
        """
        Formats the transformed data into a pretty string representation.

        Args:
            data: A list of dictionaries containing the transformed CSV data.

        Returns:
            A formatted string for easy reading.
        """
        return pformat(data, indent=2, width=80)
