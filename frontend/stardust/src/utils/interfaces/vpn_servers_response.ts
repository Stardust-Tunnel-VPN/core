/*
VPN SERVERS RESPONSE EXAMPLE:
[
    {
        "#HostName": "vpn797440165",
        "IP": "220.79.233.185",
        "Score": "649038",
        "Ping": "-",
        "Speed": "209919755",
        "CountryLong": "Korea Republic of",
        "CountryShort": "KR",
        "NumVpnSessions": "1",
        "Uptime": "182045986",
        "TotalUsers": "187",
        "TotalTraffic": "32262656957",
        "LogType": "2weeks",
        "Operator": "DESKTOP-R0MS32R's owner",
        "Message": ""
    },
    {
        "#HostName": "vpn439822420",
        "IP": "221.138.198.67",
        "Score": "588539",
        "Ping": "-",
        "Speed": "58661386",
        "CountryLong": "Korea Republic of",
        "CountryShort": "KR",
        "NumVpnSessions": "25",
        "Uptime": "101105986",
        "TotalUsers": "24615",
        "TotalTraffic": "2577926875390",
        "LogType": "2weeks",
        "Operator": "MARUNE's owner",
        "Message": ""
    },
    {
        "#HostName": "vpn375848165",
        "IP": "221.146.239.187",
        "Score": "517004",
        "Ping": "-",
        "Speed": "330161176",
        "CountryLong": "Korea Republic of",
        "CountryShort": "KR",
        "NumVpnSessions": "6",
        "Uptime": "71478986",
        "TotalUsers": "447734",
        "TotalTraffic": "28037439829789",
        "LogType": "2weeks",
        "Operator": "DESKTOP-UMTBETK's owner",
        "Message": ""
    },
    {
        "#HostName": "*\r"
    },
    ...
]    

*/

export interface IVpnServerResponse {
  '#HostName': string
  IP: string
  Score: string
  Ping: string
  Speed: string
  CountryLong: string
  CountryShort: string
  NumVpnSessions: string
  Uptime: string
  TotalUsers: string
  TotalTraffic: string
  LogType: string
  Operator: string
  Message: string
}
