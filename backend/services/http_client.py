import aiohttp
import asyncio
from loguru import logger


class HttpClient:
    """
    HTTP клиент
    """
    def __init__(self):
        self.session = None

    
    async def get_session(self):
        """
        Получение сессии
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
            logger.success("HTTP сессия создана")
        return self.session
    

    async def close(self):
        """
        Закрытие сессии
        """
        if self.session:
            await self.session.close()
            logger.success("HTTP сессия закрыта")
            self.session = None
    

    async def get(self, url, params=None, retries=3):
        """
        GET запрос
        """
        session = await self.get_session()

        for attempt in range(retries):
            try:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 429:
                        raise Exception("Превышение лимита запросов: 429")
                    response.raise_for_status()
                    return await response.json()
            
            except Exception as e:
                logger.warning(f"Ошибка при запросе: {e}. Попытка {attempt + 1}")

                if attempt == retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)


    async def post(self, url, data=None, json=None, params=None, retries=3):
        """
        POST запрос
        """
        session = await self.get_session()

        for attempt in range(retries):
            try:
                async with session.post(url, params=params, json=json, data=data, timeout=10) as response:
                    if response.status == 429:
                        raise Exception("Превышение лимита запросов: 429")
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.warning(f"Ошибка при POST запросе: {e}. Попытка {attempt + 1}")
                if attempt == retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)


    async def patch(self, url, data=None, json=None, params=None, retries=3):
        """
        PATCH запрос
        """
        session = await self.get_session()
        for attempt in range(retries):
            try:
                async with session.patch(url, params=params, json=json, data=data, timeout=10) as response:
                    if response.status == 429:
                        raise Exception("Превышение лимита запросов: 429")
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.warning(f"Ошибка при PATCH запросе: {e}. Попытка {attempt + 1}")
                if attempt == retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)


http_client = HttpClient()
