from enum import Enum


class SortField(Enum):
    HOSTNAME = ("#HostName", "text")
    IP = ("IP", "text")
    SCORE = ("Score", "numeric")
    PING = ("Ping", "numeric")
    SPEED = ("Speed", "numeric")
    COUNTRY_LONG = ("CountryLong", "text")
    COUNTRY_SHORT = ("CountryShort", "text")
    NUM_VPN_SESSIONS = ("NumVpnSessions", "numeric")
    UPTIME = ("Uptime", "numeric")
    TOTAL_USERS = ("TotalUsers", "numeric")
    TOTAL_TRAFFIC = ("TotalTraffic", "numeric")
    LOG_TYPE = ("LogType", "text")
    OPERATOR = ("Operator", "text")
    MESSAGE = ("Message", "text")

    @classmethod
    def from_key(cls, key: str) -> "SortField":
        """
        Returns the corresponding SortField for the given key string.
        Raises ValueError if no matching field is found.
        """
        for field in cls:
            if field.value[0] == key:
                return field
        raise ValueError(f"Unknown sort key: {key}")
