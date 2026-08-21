from aiohttp import ClientSession, ClientResponseError
import asyncio
from loguru import logger


class HttpClient:
    """
    HTTP клиент
    """
    def __init__(self):
        self.session = None
        self.loop = None

    
    async def get_session(self):
        """
        Получение сессии
        """
        current_loop = asyncio.get_running_loop()

        if self.session is None:
            self.session = ClientSession()
            self.loop = current_loop
            logger.success("HTTP сессия создана")
            return self.session
        
        if self.loop is not current_loop:
            logger.info("Обнаружен новый event loop. Пересоздаем HTTP сессию.")
            try:
                if not self.session.closed:
                    await self.session.close()
            except Exception as e:
                logger.exception(f"Ошибка при закрытии старой сессии: {e}")


            self.session = ClientSession()
            self.loop = current_loop
            logger.success("HTTP сессия обновлена")
        
        return self.session
    

    async def close(self):
        """
        Закрытие сессии
        """
        if self.session and not self.session.closed:
            await self.session.close()
            logger.success("HTTP сессия закрыта")
        self.session = None
        self.loop = None


    async def get(self, url, params=None, retries=3):
        """
        GET запрос с retry/backoff и обработкой 429
        """
        session = await self.get_session()

        for attempt in range(retries):
            try:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 429:
                        # если сервер вернул Retry-After, пауза по нему, иначе экспоненциальный backoff
                        retry_after = response.headers.get('Retry-After')
                        try:
                            wait = int(retry_after) if retry_after and retry_after.isdigit() else (2 ** attempt)
                        except Exception:
                            wait = 2 ** attempt
                        logger.warning(f"Получен 429 (rate limit). Ожидание {wait}s перед повтором (попытка {attempt + 1})")
                        if attempt == retries - 1:
                            response.raise_for_status()
                        await asyncio.sleep(wait)
                        continue

                    response.raise_for_status()
                    return await response.json()
            except ClientResponseError as e:
                logger.warning(f"Ошибка при запросе: {e}. Попытка {attempt + 1}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                # Ловим сетевые/таймаут/прочие ошибки и повторяем
                logger.exception(f"Ошибка при запросе: {e}. Попытка {attempt + 1}")
                if attempt == retries - 1:
                    raise
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
            except ClientResponseError as e:
                logger.warning(f"Ошибка при POST запросе: {e}. Попытка {attempt + 1}")
                if attempt == retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.exception(f"Ошибка при запросе: {e}")


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
            except ClientResponseError as e:
                logger.warning(f"Ошибка при PATCH запросе: {e}. Попытка {attempt + 1}")
                if attempt == retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.exception(f"Ошибка при запросе: {e}")


http_client = HttpClient()
