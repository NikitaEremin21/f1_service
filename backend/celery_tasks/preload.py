from celery import shared_task
from services.preload_service import PreloadService
import asyncio


@shared_task
def preload_session_data_task():
    """
    Запуск задачи на предзагрузку данных сессий
    """
    asyncio.run(PreloadService.preload_session_data())