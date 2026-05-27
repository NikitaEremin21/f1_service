from django.urls import path, include
from ninja import NinjaAPI
from api.v1.router import router as v1_router


api = NinjaAPI(title="F1 Service API", version="1.0", docs_url="/docs")

api.add_router("/v1/", v1_router)

urlpatterns = [
    path("", api.urls)
]