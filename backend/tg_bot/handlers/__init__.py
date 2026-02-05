from aiogram import Router
from .start import router as start_router
from .drivers import router as drivers_list_router


router = Router()

router.include_router(start_router)
router.include_router(drivers_list_router)