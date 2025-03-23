from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from api.router.router import main_router
import ctypes

app = FastAPI()


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    """
    Custom exception handler for ResponseValidationError.
    """
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={
            "detail": "Response validation error",
            "errors": exc.errors(),
        },
    )


app.include_router(main_router)

print("Is Admin?", is_admin())
