from fastapi import APIRouter, Depends

from api.schemas.servers_list_schema import VPNGateServersSchema
from dependencies.vpn_handler_fabric import VPNGateHandler
from dependencies.vpn_handler_fabric import get_vpngate_handler
from utils.reusable.sort_directions import SortDirection

from typing import List, Dict, Optional

router = APIRouter()


@router.get(
    "/vpn_servers_list",
    # response_model=VPNGateServersSchema
)
async def get_vpn_servers(
    handler: VPNGateHandler = Depends(get_vpngate_handler),
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    order_by: Optional[SortDirection] = SortDirection.DESC,
) -> List[Dict[str, str]]:
    """
    Returns the VPN servers from the vpngate.net website.

    Args:
        handler (VPNGateHandler): VPNGateHandler instance with all needed dependencies.

    Returns:
        List[Dict[str, str]]: The VPN servers from the vpngate.net website.
    """
    try:
        return handler.get_vpn_servers()
    except Exception as exc:
        return {"You've got an error in getting vpn server list method, ": str(exc)}
