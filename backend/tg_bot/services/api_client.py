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
        if not data:
            return None
        return data
    

    async def get_upcoming_calendar(self):
        """
        Получает календарь предстоящих гонок из бэкенда
        """
        url = f"{self.base_url}/calendar/upcoming"
        data = await http_client.get(url)
        if not data:
            return None
        return data
    

    async def get_next_race(self, user_tz):
        """
        Получить следующую гонку
        """
        url = f"{self.base_url}/calendar/next_race"
        data =await http_client.get(url, params={"user_tz": user_tz})
        if not data:
            return None
        return data
    

    async def get_all_drivers(self):
        """
        Получить список пилотов
        """
        url = f"{self.base_url}/drivers/all"
        data = await http_client.get(url)
        if not data:
            return None
        return data
    

    async def get_all_constructors(self):
        """
        Получить список команд
        """
        url = f"{self.base_url}/constructors/all"
        data = await http_client.get(url)
        if not data:
            return None
        return data
    

    async def get_standings_drivers(self):
        """
        Получить зачет пилотов
        """
        url = f"{self.base_url}/standings/drivers"
        data = await http_client.get(url)
        if not data:
            return None
        return data
    

    async def get_standings_teams(self):
        """
        Получить кубок конструкторов
        """
        url = f"{self.base_url}/standings/constructors"
        data = await http_client.get(url)
        if not data:
            return None
        return data
    

backend_client = BackendClient()