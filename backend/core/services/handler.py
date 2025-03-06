from core.services.packer import Packer
from core.services.parser import Parser

from utils.reusable.vars import request_url

from typing import List, Dict


class vpngateHandler:
    """
    Python class that handles the data from the vpngate.net website.
    """

    def __init__(self):
        self.parser = Parser(request_url)
        self.packer = Packer(self.parser.parseURL())

    def get_vpn_servers(self) -> List[Dict[str, str]]:
        """
        Returns the VPN servers from the vpngate.net website.
        """
        return self.packer.transform_content()
