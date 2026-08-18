from django.utils import timezone
from datetime import timedelta
from loguru import logger
from tg_bot.services.telegram_services import telegram_service
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
        
        max_reminder = UserSessionSubscription.objects.aggregate(
            max_reminder=models.Max('reminder_time')
        )['max_reminder'] or 60

        lookahead = now + timedelta(minutes=max_reminder)

        races = GrandPrix.objects.filter(
            Q(race_datetime__gte=now) |
            Q(qualifying_datetime__gte=now) |
            Q(fp1_datetime__gte=now) |
            Q(fp2_datetime__gte=now) |
            Q(fp3_datetime__gte=now) |
            Q(sprint_qualifying_datetime__gte=now) |
            Q(sprint_datetime__gte=now)
        ).distinct()

        notifications = []

        for race in races:
            for field in self._get_session_fields(race):
                session_time = getattr(race, field)
                if not session_time or session_time < now or session_time > lookahead:
                    continue

                session_type = field.replace('_datetime', '')
            
                subscriptions = UserSessionSubscription.objects.filter(
                    session_type=session_type,
                    user__notifications_enabled=True
                ).select_related('user')

                for sub in subscriptions:
                    reminder_time = session_time - timedelta(minutes=sub.reminder_time)
                    
                    if not reminder_time - timedelta(seconds=30) <= now <= reminder_time + timedelta(seconds=30):
                        continue

                    already_sent = NotificationLog.objects.filter(
                            user=sub.user,
                            race=race,
                            session_type=session_type,
                            reminder_time=sub.reminder_time
                        ).exists()

                    if already_sent:
                        continue

                    message = (
                        f"{GP_FLAGS.get(race.name, '🏁')} "
                        f"<b>"
                        f"{SESSION_MAP.get(session_type, session_type)} "
                        f"через {sub.reminder_time} мин."
                        f"</b>\n"
                        f"{race.name}"
                    )

                    notifications.append({
                        "user": sub.user,
                        "race": race,
                        "session_type": session_type,
                        "reminder_time": sub.reminder_time,
                        "telegram_id": sub.user.telegram_id,
                        "message": message,
                    })

        if not notifications:
            return

        telegram_messages = [
            (
                notification["telegram_id"],
                notification["message"]
            )
            for notification in notifications
        ]

        results = telegram_service.send_messages(
            telegram_messages
        )

        for notification, success in zip(
            notifications,
            results
        ):
            if not success:
                continue

            NotificationLog.objects.create(
                user=notification["user"],
                race=notification["race"],
                session_type=notification["session_type"],
                reminder_time=notification["reminder_time"]
            )

            logger.info(
                f"Уведомление отправлено пользователю "
                f"{notification['telegram_id']} "
                f"о {notification['session_type']} "
                f"за {notification['reminder_time']} мин."
            )

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
