from typing import List, Literal, Optional
from ninja import Router
from pydantic import BaseModel
from ninja.errors import HttpError
from services.user_service import (
    create_user,
    get_user_by_telegram_id,
    set_timezone
)
from services.notification_service import (
    get_enabled_sessions_and_reminders,
    delete_all_subscriptions,
    create_subscriptions
)
from core.models import SessionType


router = Router()


class UserCreateSchema(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None


class UserResponseSchema(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    timezone: str


class TimezoneSetSchema(BaseModel):
    telegram_id: int
    city: str


class NotificationSettingsSchema(BaseModel):
    type: Literal['session', 'reminder']
    value: str | int
    enabled: bool


class NotificationSettingsResponseSchema(BaseModel):
    success: bool
    enabled_sessions: List[str]
    enabled_reminders: List[int]


class SyncNotificationsSchema(BaseModel):
    enabled_sessions: List[str]
    enabled_reminders: List[int]


@router.post("/create", response=UserResponseSchema)
async def create_user_api(request, data: UserCreateSchema):
    """
    Создать пользователя (регистрация)
    """
    user = await create_user(
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
async def set_timezone_api(request, data: TimezoneSetSchema):
    """Установить часовой пояс пользователя"""
    user = await get_user_by_telegram_id(data.telegram_id)
    if not user:
        raise HttpError(404, "Пользователь не найден")
    timezone = await set_timezone(user, data.city)
    return UserResponseSchema(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        timezone=timezone or user.timezone
    )


@router.get("/{telegram_id}", response=UserResponseSchema)
async def get_user_api(request, telegram_id: int):
    """Получить пользователя по telegram_id"""
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise HttpError(404, "Пользователь не найден")
    return UserResponseSchema(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        timezone=user.timezone
    )


@router.get("/{telegram_id}/notifications", response=NotificationSettingsResponseSchema)
async def get_notifications_api(request, telegram_id):
    """Получить текущие настройки уведомлений пользователя"""
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise HttpError(404, "Пользователь не найден")

    enabled_sessions, enabled_reminders = await get_enabled_sessions_and_reminders(user)

    return {
        "success": True,
        "enabled_sessions": list(enabled_sessions),
        "enabled_reminders": list(enabled_reminders)
    }


@router.post("/{telegram_id}/notifications/sync", response=NotificationSettingsResponseSchema)
async def sync_notifications_api(request, telegram_id: int, data: SyncNotificationsSchema):
    """Полностью синхронизировать настройки уведомлений"""
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise HttpError(404, "Пользователь не найден")
    
    # Валидация
    valid_sessions = SessionType.values
    invalid_sessions = [s for s in data.enabled_sessions if s not in valid_sessions]
    if invalid_sessions:
        raise HttpError(400, f"Недопустимые типы сессий: {invalid_sessions}")
    
    valid_reminders = [120, 60, 30, 20, 15, 10]
    invalid_reminders = [r for r in data.enabled_reminders if r not in valid_reminders]
    if invalid_reminders:
        raise HttpError(400, f"Недопустимые интервалы: {invalid_reminders}")
    
    # Удаляем старые подписки
    await delete_all_subscriptions(user)
    
    # Создаём новые для всех комбинаций
    await create_subscriptions(user, data.enabled_sessions, data.enabled_reminders)
    
    return {
        "success": True,
        "enabled_sessions": data.enabled_sessions,
        "enabled_reminders": data.enabled_reminders
    }


@router.patch("/{telegram_id}/notifications", response=NotificationSettingsResponseSchema)
async def update_notifications_api(request, telegram_id, data: NotificationSettingsSchema):
    """Обновить настройки уведомлений пользователя"""
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise HttpError(404, "Пользователь не найден")

    enabled_sessions, enabled_reminders = await get_enabled_sessions_and_reminders(user)
    
    if data.type == 'session':
        value = str(data.value)
        valid_sessions = SessionType.values
        if value not in valid_sessions:
            raise HttpError(400, f"Недопустимый тип сессии: {value}")
        if data.enabled:
            enabled_sessions.add(value)
        else:
            enabled_sessions.discard(value)
    else:
        value = int(data.value)
        valid_reminders = [120, 60, 30, 20, 15, 10]
        if value not in valid_reminders:
            raise HttpError(400, f"Недопустимое время напоминания: {value}")
        if data.enabled:
            enabled_reminders.add(value)
        else:
            enabled_reminders.discard(value)
    
    await delete_all_subscriptions(user)
    await create_subscriptions(user, enabled_sessions, enabled_reminders)

    return {
        "success": True,
        "enabled_sessions": list(enabled_sessions),
        "enabled_reminders": list(enabled_reminders)
    }