from ninja import Router
from api.v1 import calendar


router = Router()


router.add_router("/calendar", calendar.router, tags=["calendar"])