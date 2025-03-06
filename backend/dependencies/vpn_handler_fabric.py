from core.services.handler import VPNGateHandler
from core.services.packer import Packer
from core.services.parser import Parser
from utils.reusable.vars import request_url


def get_vpngate_handler() -> VPNGateHandler:
    """
    Fabric method to get VPNGateHandler instance with all needed dependencies.
    """
    try:

        parser = Parser(request_url)
        packer = Packer(parser.parseURL())

        handler = VPNGateHandler(parser=parser, packer=packer)

        return handler
    except Exception as exc:
        print(f"An error occurred in vpn handler creation: {exc}")
        return None
