from django.utils import timezone
from datetime import timedelta
from loguru import logger
from tg_bot.services.telegram_services import send_message
from services.utils import SESSION_MAP


class NotificationService:
    """
    Сервис для управления уведомлениями пользователей о предстоящих событиях Гран-при.
    """
    def __init__(self):
        self.reminder_minutes = 60


    def check_and_send(self):
        """
        Проверяет предстоящие события и отправляет уведомления пользователям.
        """
        now = timezone.now()
        reminder_time = now + timedelta(minutes=self.reminder_minutes)

        upcoming_sessions = self._get_upcoming_sessions(reminder_time)

        for session in upcoming_sessions:
            self._send_for_session(session)


    def _get_upcoming_sessions(self, reminder_time):
        """
        Находит все сессии, которые начнутся в target_time.
        """
        from core.models import GrandPrix
        sessions = []
        races = GrandPrix.objects.filter(
            race_datetime__isnull=False,
        )

        for race in races:
            for session_field in self._get_session_fields(race):
                session_time = getattr(race, session_field)

                if not session_time:
                    continue

                if abs((session_time - reminder_time).total_seconds()) < 120:
                    sessions.append({
                        'race': race,
                        'session_type': session_field.replace('_datetime', ''),
                        'session_time': session_time,
                    })

        return sessions
    

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
    

    def _send_for_session(self, session):
        """
        Отправляет уведомление для указанной сессии.
        """
        from core.models import User, NotificationLog
        race = session['race']
        session_type = session['session_type']

        users = User.objects.all()

        for user in users:
            if NotificationLog.objects.filter(
                user=user,
                race=race,
                session_type=session_type,
            ).exists():
                continue

            success = self._send_notification(user, race, session_type)

            if success:
                NotificationLog.objects.create(
                    user=user,
                    race=race,
                    session_type=session_type,
                )

    
    def _send_notification(self, user, race, session_type):
        """
        Отправляет уведомление пользователю.
        """
        message = f"Внимание!\n{race.name}\nначнется через {self.reminder_minutes} минут."

        return send_message(user.telegram_id, message)
