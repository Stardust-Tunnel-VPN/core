from typing import Dict, List

from core.services.packer import Packer
from core.services.parser import Parser
from utils.reusable.vars import request_url


class VPNGateHandler:
    """
    Python class that handles the data from the vpngate.net website.
    """

    def __init__(self, parser: Parser, packer: Packer):
        self.parser = parser
        self.packer = packer

    def get_vpn_servers(self) -> List[Dict[str, str]]:
        """
        Returns the VPN servers from the vpngate.net website.
        """
        try:
            return self.packer.transform_content(order_by="DESC")
        except Exception as exc:
            return {"You've got an error in getting vpn server list method, ": str(e)}
