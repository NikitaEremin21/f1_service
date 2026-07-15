from django.utils import timezone
from datetime import timedelta
from loguru import logger


class PreloadService():
    """
    Сервис для предзагрузки данных
    """
    @staticmethod
    async def preload_session_data():
        """
        Предзагрузка данных сессий
        """
        from services.race_service import get_relevant_race

        now = timezone.now()
        race = await get_relevant_race()
        
        if race.has_sprint:
            session_fields = [
                'fp1_datetime', 'sprint_qualifying_datetime', 'sprint_datetime',
                'qualifying_datetime', 'race_datetime'
            ]
        else:
            session_fields = [
                'fp1_datetime', 'fp2_datetime', 'fp3_datetime',
                'qualifying_datetime', 'race_datetime'
            ]
        
        next_session_time = None
        for field in session_fields:
            session_time = getattr(race, field)
            if session_time and session_time > now:
                if next_session_time is None or session_time < next_session_time:
                    next_session_time = session_time
        if next_session_time is None:
            return

        time_until_next = next_session_time - now
        if time_until_next > timedelta(minutes=30):
            return

        for field in session_fields:
            session_time = getattr(race, field)
            if not session_time or session_time > now:
                continue
            await PreloadService._load_session(race, field)
    

    @staticmethod
    async def _load_session(race, field):
        """
        Загружает данные для конкретной сессии (если их нет в кэше).
        """
        from services.openf1_service import get_meeting_key, get_session_key
        from services.utils import SESSION_MAP, PRACTICE_SESSIONS
        from services.result_service import get_practice_results, get_qualifying_results, get_race_results
        
        session_type = field.replace('_datetime', '')
        try:
            meeting_key = await get_meeting_key(race.name, race.year)
        
            session_name = SESSION_MAP.get(session_type)
            session_key = await get_session_key(meeting_key, session_name, race.year)

            if session_type in PRACTICE_SESSIONS:
                await get_practice_results(session_key)
            elif session_type in ('qualifying', 'sprint_qualifying'):
                await get_qualifying_results(session_key)
            else: 
                await get_race_results(session_key)

        except Exception as e:
            logger.error(f"Ошибка предзагрузки {race.name} – {session_type}: {e}")


    @staticmethod
    async def preload_standings_data():
        """
        Предзагрузка данных чемпионата пилотов и команд
        """
        from services.race_service import get_relevant_race
        from services.openf1_service import get_meeting_key, get_session_key
        from services.race_service import get_last_completed_race

        now = timezone.now()
        race = await get_relevant_race()

        if not race:
            return
        
        if race.has_sprint:
            session_fields = [
                'fp1_datetime', 'sprint_qualifying_datetime', 'sprint_datetime',
                'qualifying_datetime', 'race_datetime'
            ]
        else:
            session_fields = [
                'fp1_datetime', 'fp2_datetime', 'fp3_datetime',
                'qualifying_datetime', 'race_datetime'
            ]

        next_session_time = None
        for field in session_fields:
            session_time = getattr(race, field)
            if session_time and session_time > now:
                if next_session_time is None or session_time < next_session_time:
                    next_session_time = session_time

        if next_session_time is None:
            return

        time_until_next = next_session_time - now
        if time_until_next > timedelta(minutes=30):
            return
        
        race_for_standings, session_type = await get_last_completed_race()

        if not race_for_standings:
            logger.error("Произошла ошибка")
            return
        
        await PreloadService._load_standings(race_for_standings, session_type)
    

    @staticmethod
    async def _load_standings(race, session_type):
        """
        Загружает таблицы пилотов и конструкторов для указанной сессии.
        """
        from services.openf1_service import get_meeting_key, get_session_key
        from services.standing_service import get_championship_drivers, get_championship_teams

        try:
            meeting_key = await get_meeting_key(race.name, race.year)
            session_key = await get_session_key(meeting_key, session_type, race.year)
            await get_championship_drivers(session_key)
            await get_championship_teams(session_key)
        except Exception as e:
            logger.error(f"При загрузке данных проишла ошибка: {e}")