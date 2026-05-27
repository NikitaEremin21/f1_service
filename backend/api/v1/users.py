from ninja import Router
from pydantic import BaseModel
from asgiref.sync import sync_to_async
from ninja.errors import HttpError
from services.user_service import (
    create_user,
    get_user_by_telegram_id,
    set_timezone
)
from loguru import logger


router = Router()


class UserCreateSchema(BaseModel):
    telegram_id: int
    username: str
    first_name: str


class UserResponseSchema(BaseModel):
    telegram_id: int
    username: str
    first_name: str
    timezone: str


class TimezoneSetSchema(BaseModel):
    telegram_id: int
    city: str


@router.post("/create", response=UserResponseSchema)
async def create_user_api(request, data: UserCreateSchema):
    """
    Создать пользователя (регистрация)
    """
    user = await sync_to_async(create_user)(
        data.telegram_id,
        data.username,
        data.first_name
    )
    return UserResponseSchema(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        timezone=user.timezone
    )


@router.post("/set_timezone", response=UserResponseSchema)
def set_timezone_api(request, data: TimezoneSetSchema):
    """Установить часовой пояс пользователя"""
    logger.debug(data)
    user = get_user_by_telegram_id(data.telegram_id)
    if not user:
        raise HttpError(404, "Пользователь не найден")
    timezone = set_timezone(user, data.city)
    return UserResponseSchema(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        timezone=timezone or user.timezone
    )


@router.get("/{telegram_id}", response=UserResponseSchema)
def get_user_api(request, telegram_id: int):
    """Получить пользователя по telegram_id"""
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        raise HttpError(404, "Пользователь не найден")
    return UserResponseSchema(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        timezone=user.timezone
    )
