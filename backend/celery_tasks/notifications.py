from celery import shared_task
from services.notification_service import NotificationService


@shared_task
def check_and_send_notifications():
    """
    Запуск задачи по отправке уведомлений
    """
    NotificationService().check_and_send()