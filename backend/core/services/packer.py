import traceback
from pprint import pformat
from typing import Dict, List, Optional

from fastapi import HTTPException

from utils.reusable.filters import filters_VPN_GATE
from utils.reusable.restricted_countries import RestrictedCountries
from utils.reusable.sort_directions import SortDirection
from utils.reusable.sorted_keys import SortField


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
                index
                for index, header in enumerate(headers)
                if header in allowed_fields
            ]

            allowed_header_names = [headers[i] for i in allowed_indices]

            transformed_data: List[Dict[str, str]] = []

            for line in csv_lines[2:]:
                if not line.strip():
                    continue
                row_values = line.split(",")
                row_dict = {}
                for allowed_index, header_name in zip(
                    allowed_indices, allowed_header_names
                ):
                    if allowed_index < len(row_values):
                        row_dict[header_name] = row_values[allowed_index]
                transformed_data.append(row_dict)

            transformed_data = [
                row
                for row in transformed_data
                if row.get("#HostName", "").strip() != "*"
            ]

            if search:
                transformed_data = self.filter_by_hostname(
                    data=transformed_data, search=search
                )

            if sort_by:
                sort_field = (
                    sort_by
                    if isinstance(sort_by, SortField)
                    else SortField.from_key(sort_by)
                )
                transformed_data = self.sort_content(
                    data=transformed_data,
                    direction=order_by if order_by else SortDirection.DESC,
                    sort_key=sort_field,
                )

            transformed_data = self.remove_restricted_countries(data=transformed_data)
            return transformed_data

        except Exception as exc:
            print("Error in content trasnformation method: ", str(exc))
            traceback.print_exc()
            return []

    def sort_text(
        self, data: List[Dict[str, str]], sort_key: str, reverse: bool = True
    ) -> List[Dict[str, str]]:
        """
        Sorts the data lexicographically based on the given sort_key.

        Args:
            data: List of dictionaries representing CSV rows.
            sort_key: The key in the dictionary to sort by.
            reverse: Whether to sort in descending order; default is True.

        Returns:
            A new list of dictionaries sorted lexicographically (case-insensitive).
        """
        return sorted(
            data, key=lambda row: row.get(sort_key, "").lower(), reverse=reverse
        )

    def sort_num(
        self, data: List[Dict[str, str]], sort_key: str, reverse: bool = True
    ) -> List[Dict[str, str]]:
        """
        Sorts the data numerically based on the given sort_key.

        If a value cannot be converted to a float, it defaults to 0.0.

        Args:
            data: List of dictionaries representing CSV rows.
            sort_key: The key in the dictionary to sort by.
            reverse: Whether to sort in descending order; default is True.

        Returns:
            A new list of dictionaries sorted numerically.
        """

        def num_value(row: Dict[str, str]) -> float:
            try:
                return float(row.get(sort_key, "0"))
            except ValueError:
                return 0.0

        return sorted(data, key=num_value, reverse=reverse)

    def sort_content(
        self,
        data: List[Dict[str, str]],
        sort_key: SortField,
        direction: SortDirection = SortDirection.DESC,
    ) -> List[Dict[str, str]]:
        """
        Determines the type of the sort_key (numeric or text) based on the first non-empty value,
        and sorts the data accordingly.

        Args:
            data: List of dictionaries representing CSV rows.
            sort_key: The key in the dictionary to sort by.
            direction: Sort direction (default is descending).

        Returns:
            A new list of dictionaries sorted based on the determined type.
        """
        reverse = direction == SortDirection.DESC

        key_name, field_type = sort_key.value

        try:
            if field_type == "numeric":
                return self.sort_num(data, key_name, reverse)
            else:
                return self.sort_text(data, key_name, reverse)
        except Exception as exc:
            print("Error in sorting content method: ", str(exc))
            traceback.print_exc()
            return []

    def filter_by_hostname(
        self, data: List[Dict[str, str]], search: str
    ) -> List[Dict[str, str]]:
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

    def remove_restricted_countries(
        self, data: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Filters out VPN servers from restricted countries (for now they are Russia and Iran);
        It is dangerous to use VPN servers from these countries because they can be controlled by their government.

        Args:
            data: A list of dictionaries containing the transformed CSV data.

        Returns:
            A list of dictionaries containing the filtered data.
        """
        try:
            restricted = [country.value for country in RestrictedCountries]
            filtered_data = [
                row for row in data if row.get("CountryShort", "") not in restricted
            ]
            return filtered_data
        except Exception as exc:
            print("Error in filtering out restricted countries: ", str(exc))
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
