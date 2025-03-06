from fastapi import APIRouter
from api.endpoints.vpn_connector import router as vpn_connector_router

"""
Python module to define main API router. 
It includes all the API routers in the application.
"""

main_router = APIRouter()
main_router.include_router(
    vpn_connector_router, prefix="/api/v1", tags=["VPN Connector", "VPN Servers", "VPNGate"]
)
