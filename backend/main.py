from fastapi import APIRouter, FastAPI, Request
from api.router.router import main_router
from fastapi.responses import JSONResponse
from fastapi.exceptions import ResponseValidationError
from starlette.status import HTTP_400_BAD_REQUEST


app = FastAPI()


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    """
    Кастомный обработчик для ResponseValidationError.
    Отдаём 400 (или 422), плюс формируем более понятный текст.
    """
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={
            "detail": "Response validation error",
            "errors": exc.errors(),
        },
    )


app.include_router(main_router)
