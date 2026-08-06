from services.http_client import http_client
from django.conf import settings


class BackendClient:
    def __init__(self):
        if settings.DEBUG:
            self.base_url = "http://localhost:8000/api/v1"
        else:
            self.base_url = "http://backend:8000/api/v1"


    async def get_calendar(self):
        """
        Получает календарь гонок из бэкенда
        """
        url = f"{self.base_url}/calendar/all"
        data = await http_client.get(url)
        return data if isinstance(data, list) else []
    

    async def get_upcoming_calendar(self):
        """
        Получает календарь предстоящих гонок из бэкенда
        """
        url = f"{self.base_url}/calendar/upcoming"
        data = await http_client.get(url)
        return data if isinstance(data, list) else []
    

    async def get_next_race(self, user_tz):
        """
        Получить следующую гонку
        """
        url = f"{self.base_url}/calendar/next_race"
        data =await http_client.get(url, params={"user_tz": user_tz})
        return data
    

    async def get_all_drivers(self):
        """
        Получить список пилотов
        """
        url = f"{self.base_url}/drivers/all"
        data = await http_client.get(url)
        return data if isinstance(data, list) else []
    

    async def get_all_constructors(self):
        """
        Получить список команд
        """
        url = f"{self.base_url}/constructors/all"
        data = await http_client.get(url)
        return data if isinstance(data, list) else []
    

    async def get_standings_drivers(self):
        """
        Получить зачет пилотов
        """
        url = f"{self.base_url}/standings/drivers"
        data = await http_client.get(url)
        return data if isinstance(data, dict) else {"year": 0, "standings": []}
    

    async def get_standings_teams(self):
        """
        Получить кубок конструкторов
        """
        url = f"{self.base_url}/standings/constructors"
        data = await http_client.get(url)
        return data if isinstance(data, dict) else {"year": 0, "standings": []}


    async def get_relevant_race(self):
        """
        Получить релевантный Гран-при для отображения результатов
        """
        url = f"{self.base_url}/results/relevant_race"
        data = await http_client.get(url)
        return data
    

    async def get_session_results(self, round, session):
        """
        Получить результаты сессии по раунду и типу сессии
        """
        url = f"{self.base_url}/results/{round}/{session}"
        data = await http_client.get(url)
        if data is None:
            return None
        return data
    

    async def create_user(self, telegram_id: int, username: str = None, first_name: str = None):
        """
        Зарегистрировать пользователя
        """
        url = f"{self.base_url}/users/create"
        return await http_client.post(url, json={
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name
        })


    async def get_user(self, telegram_id: int):
        """
        Получить пользователя
        """
        url = f"{self.base_url}/users/{telegram_id}"
        return await http_client.get(url)


    async def set_user_timezone(self, telegram_id: int, city: str):
        """
        Установить часовой пояс
        """
        url = f"{self.base_url}/users/set_timezone"
        return await http_client.post(url, json={
            "telegram_id": telegram_id,
            "city": city
        })
    

    async def get_notifications(self, telegram_id):
        """
        Получить текущие настройки уведомлений пользователя
        """
        url = f"{self.base_url}/users/{telegram_id}/notifications"
        return await http_client.get(url)
    

    async def sync_notifications(self, telegram_id: int, enabled_sessions: list, enabled_reminders: list):
        """Полная синхронизация настроек уведомлений"""
        url = f"{self.base_url}/users/{telegram_id}/notifications/sync"
        data = {
            "enabled_sessions": enabled_sessions,
            "enabled_reminders": enabled_reminders
        }
        return await http_client.post(url, json=data)
    

    async def update_notifications(self, telegram_id, type, value, enabled):
        """
        Обновить настройки уведомлений пользователя
        """
        url = f"{self.base_url}/users/{telegram_id}/notifications"
        return await http_client.patch(url, json={
            "type": type,
            "value": value,
            "enabled": enabled
        })


backend_client = BackendClient()