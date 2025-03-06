from typing import List, Dict, Optional
from utils.reusable.filters import filters_VPN_GATE
import traceback
from pprint import pformat
from utils.reusable.sort_directions import SortDirection


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

    def transform_content(
        self,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        order_by: Optional[SortDirection] = SortDirection.DESC,
    ) -> List[Dict[str, str]]:
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
                    continue
                row_values = line.split(",")
                row_dict = {}
                for allowed_index, header_name in zip(allowed_indices, allowed_header_names):
                    # if the iterated row ([value1, value2, valueN, ...]) has more values ​​than the iteration index (this means that the subsequent index value goes beyond the values ​​of this row, i.e. there must be a situation where allowed_index must BE INCLUDED in the number of row values ​​(len(row_values)), otherwise during iteration it will simply go beyond the indices and assign something incorrectly)
                    if allowed_index < len(row_values):
                        row_dict[header_name] = row_values[allowed_index]
                transformed_data.append(row_dict)

            if search:
                transformed_data = self.filter_by_hostname(data=transformed_data, search=search)

            if sort_by:
                transformed_data = self.sort_content(
                    data=transformed_data,
                    direction=SortDirection.DESC if not order_by else order_by,
                    sort_key=sort_by,
                )

            return self.format_content(transformed_data)

        except Exception as exc:
            print("Error in content trasnformation method:", str(exc))
            traceback.print_exc()
            return []

    def sort_content(
        self,
        data: List[Dict[str, str]],
        direction: SortDirection = SortDirection.DESC,
        sort_key: str = "Ping",
    ) -> List[Dict[str, str]]:
        """
        Sorts the transformed data based on the 'Score' field.

        Args:
            data: A list of dictionaries containing the transformed CSV data.

        Returns:
            A sorted list of dictionaries.
        """

        def key_func(row: Dict[str, str]) -> str:
            return row.get(sort_key, "")

        is_reversed = direction == SortDirection.DESC

        try:
            # why it works like that?
            sorted_data = sorted(data, key=key_func, reverse=is_reversed)
        except Exception as exc:
            print("Error in sorting content method: ", str(exc))
            traceback.print_exc()
            return []

    def filter_by_hostname(self, data: List[Dict[str, str]], search: str) -> List[Dict[str, str]]:
        """
        Filters the transformed data based on input filters criterias.

        Args:
            data: A list of dictionaries containing the transformed CSV data.
            search: Search string. (should work with hostname header only)

        Returns:
            A sorted list of dictionaries.
        """
        try:
            result = []
            for row in data:
                if search.lower() in row.get("#HostName", "").lower():
                    result.append(row)
            return result
        except Exception as exc:
            print("Error in filtering content method: ", str(exc))
            traceback.print_exc()
            return []

    def format_content(self, data: List[Dict[str, str]]) -> str:
        """
        Formats the transformed data into a pretty string representation.

        Args:
            data: A list of dictionaries containing the transformed CSV data.

        Returns:
            A formatted string for easy reading.
        """
        return pformat(data, indent=2, width=80)
