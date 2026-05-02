import aiohttp
import asyncio
from loguru import logger


class HttpClient:
    def __init__(self):
        self.session = None

    
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    

    async def get(self, url, params=None, retries=3):
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

    
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None


http_client = HttpClient()
