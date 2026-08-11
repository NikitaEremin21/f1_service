from celery import shared_task
from services.notification_service import NotificationService
import asyncio


@shared_task
def check_and_send_notifications():
    """
    Запуск задачи по отправке уведомлений
    """
    asyncio.run(NotificationService().check_and_send())