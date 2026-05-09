from ninja import Router
from api.v1 import calendar
from api.v1 import drivers


router = Router()


router.add_router("/calendar", calendar.router, tags=["calendar"])
router.add_router("/drivers", drivers.router, tags=["drivers"])