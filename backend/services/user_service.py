from core.models import User
from services.utils import get_timezone_by_city


def create_user(telegram_id, username, first_name):
    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": username,
            "first_name": first_name,
        }
    )
    return user


def get_user_by_telegram_id(telegram_id):
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None
    
    
def set_timezone(user, city):
    timezone = get_timezone_by_city(city)
    if not timezone:
        return None
    
    user.timezone = timezone
    user.save(update_fields=["timezone"])

    return timezone



    