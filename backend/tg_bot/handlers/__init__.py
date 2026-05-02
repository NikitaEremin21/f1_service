from aiogram import Router
from .start import router as start_router
from .drivers import router as drivers_list_router
from .constructors import router as constructors_list_router
from .calendar import router as calendar_router
from .results import router as results_router
from .standings import router as standings_router
from .settings import router as settings_router


router = Router()

router.include_router(start_router)
router.include_router(drivers_list_router)
router.include_router(constructors_list_router)
router.include_router(calendar_router)
router.include_router(results_router)
router.include_router(standings_router)
router.include_router(settings_router)