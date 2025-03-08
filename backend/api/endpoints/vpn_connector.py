from typing import Dict, List, Optional

from fastapi import APIRouter, Depends

from api.schemas.servers_list_schema import VPNGateServersSchema
from dependencies.vpn_handler_fabric import VPNGateHandler, get_vpngate_handler
from utils.reusable.sort_directions import SortDirection

router = APIRouter()


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
