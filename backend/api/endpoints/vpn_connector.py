from typing import Dict, List, Optional

from fastapi import APIRouter, Depends

from api.schemas.servers_list_schema import VPNGateServersSchema
from core.interfaces.ivpn_connector import IVpnConnector
from core.managers.vpn_manager_macos import MacOSL2TPConnector
from core.managers.vpn_manager_win import WindowsL2TPConnector
from dependencies.vpn_handler_fabric import VPNGateHandler, get_vpngate_handler
from dependencies.vpn_manager_fabric import get_vpn_connector
from utils.reusable.sort_directions import SortDirection

import logging

router = APIRouter()

connector_instance: IVpnConnector = get_vpn_connector()


# TODO: pass the server-ip logic to pydantic
@router.post("/connect")
async def connect_to_vpn(
    server_ip: str,
    kill_switch_enabled: Optional[bool] = False,
):
    """
    Connect to the given VPN server using L2TP/IPSec.

    Args:
        server_ip (str): The VPN server IP or hostname.
        username (str): The username for the VPN connection. Defaults to "vpn".
        password (str): The password for the VPN connection. Defaults to "vpn".
        psk (str): Pre-shared key for IPSec, typically 'vpn'. Defaults to "vpn".
        connector (IVpnConnector): The VPN connector instance.

    Raises:
        Exception: If failed to connect.
    """
    try:

        if isinstance(connector_instance, WindowsL2TPConnector):
            print("Ip: ", server_ip)
            result = connector_instance.connect(server_ip=server_ip)
        elif isinstance(connector_instance, MacOSL2TPConnector):
            result = await connector_instance.connect(server_ip=server_ip)
        else:
            raise Exception("Unsupported OS")

        if kill_switch_enabled:
            if isinstance(connector_instance, MacOSL2TPConnector):
                connector_instance.start_kill_switch_monitor(interval=2.0)
            elif isinstance(connector_instance, WindowsL2TPConnector):
                connector_instance.enable_kill_switch(server_ip=server_ip)

        return result
    except Exception as exc:
        logging.exception("Failed to connect to VPN")
        return {"error": f"Could not connect: {exc}"}


@router.post("/disconnect")
async def disconnect_from_vpn(
    server_ip: Optional[str] = None,
) -> str:
    """
    Disconnect from the given VPN server.

    Args:
        server_ip (str): The VPN server IP or name used previously.
        connector (IVpnConnector): The VPN connector instance.

    Raises:
        Exception: If failed to disconnect.
    """
    try:
        # if isinstance(connector_instance, MacOSL2TPConnector):
        #     connector_instance.stop_kill_switch_monitor()

        return await connector_instance.disconnect(server_ip=server_ip)
    except Exception as exc:
        return {"You've got an error in disconnect from vpn method, ": str(exc)}


@router.get("/status")
async def check_vpn_status(server_ip: Optional[str] = None) -> str:
    """
    Check if the given server is connected or not.

    Args:
        server_ip (str): The VPN server IP or name.
        connector (IVpnConnector): The VPN connector instance.

    Returns:
        str: The status of the VPN connection.
    """
    try:
        return await connector_instance.status(server_ip=server_ip)
    except Exception as exc:
        return {"You've got an error in check vpn status method, ": str(exc)}


@router.post("/enable_kill_switch")
async def enable_kill_switch() -> None:
    """
    Enable kill switch, blocking all traffic outside VPN.

    Args:
        connector (IVpnConnector): The VPN connector instance.

    Raises:
        Exception: If failed to enable kill switch.
    """
    try:
        return await connector_instance.enable_kill_switch()
    except Exception as exc:
        return {"You've got an error in enable kill switch method, ": str(exc)}


@router.post("/disable_kill_switch")
async def disable_kill_switch() -> str:
    """
    Disable kill switch, restore normal network.

    Args:
        connector (IVpnConnector): The VPN connector instance.

    Raises:
        Exception: If failed to disable kill switch.
    """
    try:
        return await connector_instance.disable_kill_switch()
    except Exception as exc:
        return {"You've got an error in disable kill switch method, ": str(exc)}


@router.get(
    "/vpn_servers_list",
    # response_model=VPNGateServersSchema
)
async def get_vpn_servers(
    handler: VPNGateHandler = Depends(get_vpngate_handler),
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    order_by: Optional[SortDirection] = SortDirection.ASC,
) -> List[Dict[str, str]]:
    """
    Returns the VPN servers from the vpngate.net website.

    Args:
        handler (VPNGateHandler): VPNGateHandler instance with all needed dependencies.

    Returns:
        List[Dict[str, str]]: The VPN servers from the vpngate.net website.
    """
    try:
        return handler.get_vpn_servers(search=search, sort_by=sort_by, order_by=order_by)
    except Exception as exc:
        return {"You've got an error in getting vpn server list method, ": str(exc)}
