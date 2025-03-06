from typing import List, Optional

from pydantic import BaseModel, Field


class VPNGateServer(BaseModel):
    HostName: Optional[str] = Field(None, alias="#HostName")
    IP: Optional[str]
    Score: Optional[str]
    Ping: Optional[str]
    Speed: Optional[str]
    CountryLong: Optional[str]
    CountryShort: Optional[str]
    NumVpnSessions: Optional[str]
    Uptime: Optional[str]
    TotalUsers: Optional[str]
    TotalTraffic: Optional[str]
    LogType: Optional[str]
    Operator: Optional[str]
    Message: Optional[str]
    # OpenVPN_ConfigData_Base64: Optional[str] = Field(None, alias="OpenVPN_ConfigData_Base64\r")


class VPNGateServersSchema(BaseModel):
    servers: List[VPNGateServer]
