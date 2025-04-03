import asyncio

"""
Python configuration snippet for creating a new L2TP VPN connection on Windows.
"""


async def create_windows_l2tp(server_ip: str, name: str = "MyL2TP", psk: str = "vpn"):
    """
    Create a new L2TP VPN connection on Windows. Requires elevated privileges.

    Args:
        server_ip (str): The IP address of the VPN server.
        name (str): The name of the VPN connection. Defaults to "MyL2TP".
        psk (str): The pre-shared key for the connection. Defaults to "vpn".

    Returns:
        str: The output of the Add-VpnConnection cmdlet.
    """
    try:
        cmd = [
            "powershell",
            "-Command",
            f"""
            Add-VpnConnection -Name '{name}' -ServerAddress '{server_ip}' -TunnelType L2TP `
            -L2tpPsk '{psk}' -AuthenticationMethod Pap,CHAP,MSCHAPv2 -AllUserConnection -Force
            """,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to create VPN connection: {stderr.decode()}")
        return stdout.decode()
    except Exception as exc:
        print(
            f"Failed to create VPN connection for Windows (L2TP Configuration): {exc}"
        )
        raise exc
