import os

from django.urls import path, include
from ninja import NinjaAPI
from api.v1.router import router as v1_router

# В проде не публикуем ни Swagger, ни openapi.json: схема раскрывает все
# эндпоинты (включая /api/v1/users/*) и не нужна ни боту, ни пользователям.
# В dev оставляем, чтобы было удобно смотреть API.
IS_PRODUCTION = os.getenv("DJANGO_ENV", "development") == "production"

api = NinjaAPI(
    title="F1 Service API",
    version="1.0",
    docs_url=None if IS_PRODUCTION else "/docs",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)

api.add_router("/v1/", v1_router)

urlpatterns = [
    path("", api.urls)
]