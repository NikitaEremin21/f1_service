from core.models import User
from services.utils import get_timezone_by_city
from channels.db import database_sync_to_async


@database_sync_to_async
def create_user(telegram_id, username, first_name):
    """
    Создаёт нового пользователя или возвращает существующего
    """
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": username,
            "first_name": first_name,
        }
    )
    return user


@database_sync_to_async
def get_user_by_telegram_id(telegram_id):
    """
    Получает пользователя по Telegram ID.
    """
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None
    

@database_sync_to_async
def _update_user_timezone(user, timezone):
    """
    Вспомогательная синхронная функция для обновления timezone
    """
    user.timezone = timezone
    user.save(update_fields=["timezone"])
    return timezone


async def set_timezone(user, city):
    """
    функция для обновления timezone
    """
    timezone = await get_timezone_by_city(city)
    if not timezone:
        return None

    return await _update_user_timezone(user, timezone)



    