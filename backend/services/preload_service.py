from django.utils import timezone
from datetime import timedelta
from loguru import logger
from services.cache.redis_cache import redis_client


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
        if time_until_next > timedelta(minutes=60):
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
        if await PreloadService._is_preloaded_session(race, session_type):
            logger.info(f"{race.name} {session_type} уже предзагружена")
            return
        
        try:
            meeting_key = await get_meeting_key(race.name, race.year)
        
            session_name = SESSION_MAP.get(session_type)
            session_key = await get_session_key(meeting_key, session_name, race.year)

            await redis_client.delete(f'openf1:session_result:{session_key}')
            await redis_client.delete(f'openf1:driver:{session_key}')

            if session_type in PRACTICE_SESSIONS:
                await get_practice_results(session_key)
            elif session_type in ('qualifying', 'sprint_qualifying'):
                await get_qualifying_results(session_key)
            else: 
                await get_race_results(session_key)
            await PreloadService._mark_preloaded_session(race, session_type)
        except Exception as e:
            logger.exception(f"Ошибка предзагрузки {race.name} – {session_type}: {e}")


    @staticmethod
    def _session_preload_key(race, session_type):
        return f"preload:session:{race.year}:{race.name}:{session_type}"
    

    @staticmethod
    async def _is_preloaded_session(race, session_type):
        key = PreloadService._session_preload_key(race, session_type)
        cached = await redis_client.get(key)
        return cached is not None


    @staticmethod
    async def _mark_preloaded_session(race, session_type):
        key = PreloadService._session_preload_key(race, session_type)
        await redis_client.set(key, "1", 12600)


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
        if time_until_next > timedelta(minutes=60):
            return
        
        race_for_standings, session_type = await get_last_completed_race()

        if not race_for_standings:
            logger.exception("Произошла ошибка")
            return
        
        await PreloadService._load_standings(race_for_standings, session_type)
    

    @staticmethod
    async def _load_standings(race, session_type):
        """
        Загружает таблицы пилотов и конструкторов для указанной сессии.
        """
        from services.openf1_service import get_meeting_key, get_session_key
        from services.standing_service import get_championship_drivers, get_championship_teams
        
        drivers_loaded = await PreloadService._is_preloaded_standings(
            race, "championship_drivers"
        )
        teams_loaded = await PreloadService._is_preloaded_standings(
            race, "championship_teams"
        )
        if drivers_loaded and teams_loaded:
            logger.info("Таблицы уже предзагружены")
            return
        
        try:
            meeting_key = await get_meeting_key(race.name, race.year)
            session_key = await get_session_key(meeting_key, session_type, race.year)

            if not drivers_loaded:
                await redis_client.delete(f'openf1:championship_drivers:{session_key}')
                await get_championship_drivers(session_key)
                await PreloadService._mark_preloaded_standings(race, "championship_drivers")

            if not teams_loaded:
                await redis_client.delete(f'openf1:championship_teams:{session_key}')
                await get_championship_teams(session_key)
                await PreloadService._mark_preloaded_standings(race, "championship_teams")
        except Exception as e:
            logger.exception(f"При загрузке данных произошла ошибка: {e}")


    @staticmethod
    def _standings_preload_key(race, standings_type):
        return f"preload:{standings_type}:{race.year}:{race.name}"


    @staticmethod
    async def _is_preloaded_standings(race, standings_type):
        key = PreloadService._standings_preload_key(race, standings_type)
        cached = await redis_client.get(key)
        return cached is not None


    @staticmethod
    async def _mark_preloaded_standings(race, standings_type):
        key = PreloadService._standings_preload_key(race, standings_type)
        await redis_client.set(key, "1", 12600)