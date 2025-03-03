from core.services.handler import vpngateHandler

if __name__ == "__main__":
    handler = vpngateHandler()
    print(handler.get_vpn_servers())
