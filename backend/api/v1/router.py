from ninja import Router
from api.v1 import calendar
from api.v1 import drivers
from api.v1 import constructors
from api.v1 import standings
from api.v1 import results


router = Router()


router.add_router("/calendar", calendar.router, tags=["calendar"])
router.add_router("/drivers", drivers.router, tags=["drivers"])
router.add_router("/constructors", constructors.router, tags=["constructors"])
router.add_router("/standings", standings.router, tags=["standings"])
router.add_router("/results", results.router, tags=["results"])