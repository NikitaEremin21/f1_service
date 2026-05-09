from ninja import Router
from api.v1 import calendar
from api.v1 import drivers
from api.v1 import constructors


router = Router()


router.add_router("/calendar", calendar.router, tags=["calendar"])
router.add_router("/drivers", drivers.router, tags=["drivers"])
router.add_router("/constructors", constructors.router, tags=["constructors"])