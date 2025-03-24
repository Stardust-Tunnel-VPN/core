"""
Python module that stores the mapping of reusable terminal commands for VPN execution on Windows (using rasdial tool).

"""

from enum import Enum


class RasdialL2TP_Scripts(Enum):
    """
    Enum class that stores the rasdial commands for L2TP VPN connection.

    Constants:
        ADD_VPN_CONNECTION_SCRIPT (str): PowerShell script to add a new VPN connection.

        SET_VPN_CONNECTION_SCRIPT (str): PowerShell script to set an existing VPN connection.
    """

    ADD_VPN_CONNECTION_SCRIPT = """
        try {{
            Import-Module RemoteAccess -ErrorAction SilentlyContinue
            Add-VpnConnection -Name '{name}' -ServerAddress '{server_ip}' -TunnelType L2TP -L2tpPsk '{psk}' `
                -AuthenticationMethod Pap,CHAP,MSCHAPv2 -AllUserConnection -Force -ErrorAction Stop
            Write-Host "Add-VpnConnection completed successfully."
        }}
        catch {{
            Write-Host ("Error: " + $_.Exception.Message)
            exit 1
        }}
    """

    SET_VPN_CONNECTION_SCRIPT = """
        try {{
                Import-Module RemoteAccess -ErrorAction SilentlyContinue
                Set-VpnConnection -Name '{name}' -ServerAddress '{server_ip}' -TunnelType L2TP -L2tpPsk '{psk}' `
                    -AuthenticationMethod Pap,CHAP,MSCHAPv2 -AllUserConnection -Force -ErrorAction Stop
                Write-Host "Set-VpnConnection completed successfully."
            }}
            catch {{
                Write-Host ("Error: " + $_.Exception.Message)
                exit 1
            }}
    """
