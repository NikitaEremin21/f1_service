from django.utils import timezone
from datetime import timedelta
from loguru import logger
from tg_bot.services.telegram_services import send_message
from services.utils import SESSION_MAP, GP_FLAGS
from channels.db import database_sync_to_async
from django.db.models import Q
from django.db import models


class NotificationService:
    """
    Сервис для управления уведомлениями пользователей о предстоящих событиях Гран-при.
    """


    def check_and_send(self):
        from core.models import GrandPrix, UserSessionSubscription, NotificationLog
        now = timezone.now()
        # Определяем максимальный интервал подписок (поле reminder_time)
        max_reminder = UserSessionSubscription.objects.aggregate(
            max_reminder=models.Max('reminder_time')
        )['max_reminder'] or 60
        lookahead = now + timedelta(minutes=max_reminder)

        # Получаем все сессии, которые начнутся в течение lookahead
        races = GrandPrix.objects.filter(
            Q(race_datetime__gte=now) |
            Q(qualifying_datetime__gte=now) |
            Q(fp1_datetime__gte=now) |
            Q(fp2_datetime__gte=now) |
            Q(fp3_datetime__gte=now) |
            Q(sprint_qualifying_datetime__gte=now) |
            Q(sprint_datetime__gte=now)
        ).distinct()

        for race in races:
            session_fields = self._get_session_fields(race)
            for field in session_fields:
                session_time = getattr(race, field)
                if not session_time or session_time < now or session_time > lookahead:
                    continue

                session_type = field.replace('_datetime', '')
                # Находим всех пользователей, подписанных на эту сессию
                subscriptions = UserSessionSubscription.objects.filter(
                    session_type=session_type,
                    user__notifications_enabled=True
                ).select_related('user')

                for sub in subscriptions:
                    reminder_time = session_time - timedelta(minutes=sub.reminder_time)
                    # Отправляем, если reminder_time попал в текущую минуту (окно ±30 секунд для надёжности)
                    if now >= reminder_time - timedelta(seconds=30) and now <= reminder_time + timedelta(seconds=30):
                        # Проверяем, не отправляли ли уже это напоминание
                        if not NotificationLog.objects.filter(
                            user=sub.user,
                            race=race,
                            session_type=session_type,
                            reminder_time=sub.reminder_time
                        ).exists():
                            success = self._send_notification(sub.user, race, session_type, sub.reminder_time)
                            if success:
                                NotificationLog.objects.create(
                                    user=sub.user,
                                    race=race,
                                    session_type=session_type,
                                    reminder_time=sub.reminder_time
                                )
                                logger.info(f"Уведомление отправлено пользователю {sub.user.telegram_id} о {session_type} за {sub.reminder_time} мин.")
    

    def _get_session_fields(self, race):
        """
        Возвращает список полей сессий для данного Гран-при.
        """
        if race.has_sprint:
            fields = [
                'fp1_datetime',
                'sprint_qualifying_datetime',
                'sprint_datetime',
                'qualifying_datetime',
                'race_datetime',
            ]
        else:
            fields = [
                'fp1_datetime',
                'fp2_datetime',
                'fp3_datetime',
                'qualifying_datetime',
                'race_datetime',
            ]
        
        return fields

    
    def _send_notification(self, user, race, session_type, reminder_time):
        message = (
            f"{GP_FLAGS.get(race.name, '🏁') } <b>{SESSION_MAP.get(session_type, session_type)} через {reminder_time} мин.</b>\n"
            f"{race.name}"
        )
        try:
            send_message(user.telegram_id, message)
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")
            return False
    

@database_sync_to_async
def get_enabled_sessions_and_reminders(user):
    """
    Получить множества включённых сессий и интервалов для пользователя.
    """
    from core.models import UserSessionSubscription
    subscriptions = UserSessionSubscription.objects.filter(user=user)
    enabled_sessions = {sub.session_type for sub in subscriptions}
    enabled_reminders = {sub.reminder_time for sub in subscriptions}
    return enabled_sessions, enabled_reminders


@database_sync_to_async
def delete_all_subscriptions(user):
    """
    Удалить все подписки пользователя.
    """
    from core.models import UserSessionSubscription
    UserSessionSubscription.objects.filter(user=user).delete()


@database_sync_to_async
def create_subscriptions(user, sessions, reminders):
    """
    Создать подписки для всех комбинаций сессий и интервалов.
    """
    from core.models import UserSessionSubscription
    subscriptions = [
        UserSessionSubscription(user=user, session_type=session, reminder_time=reminder)
        for session in sessions
        for reminder in reminders
    ]
    UserSessionSubscription.objects.bulk_create(subscriptions)
