from aiogram import Router
from .calendar import router as calendar_router
from .upcoming import router as upcoming_router
from .next_race import router as next_race_router


router = Router()


router.include_router(calendar_router)
router.include_router(upcoming_router)
router.include_router(next_race_router)