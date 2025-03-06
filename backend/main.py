from fastapi import APIRouter, FastAPI

from core.services.handler import vpngateHandler

app = FastAPI()

app_router = APIRouter()
app.include_router(app_router)


if __name__ == "__main__":
    handler = vpngateHandler()
    print(handler.get_vpn_servers())
