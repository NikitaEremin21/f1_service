from urllib.request import urlopen
from urllib.parse import quote
import json
from loguru import logger


def get_meeting_key(meeting_name, year):
    try:
        response = urlopen(f'https://api.openf1.org/v1/meetings?year={year}&meeting_name={quote(meeting_name)}')
        data = json.loads(response.read().decode('utf-8'))
        meeting_key = data[0].get('meeting_key')
        return meeting_key
    except Exception as e:
        logger.warning(
            f"Ошибка при получении meeting_key для {meeting_name}"
        )
        raise e
    

def get_session_key(meeting_key, session_name, year):
    try:
        response = urlopen(f'https://api.openf1.org/v1/sessions?'
                           f'meeting_key={meeting_key}&session_name={quote(session_name)}&year={year}')
        data = json.loads(response.read().decode('utf-8'))
        session_key = data[0].get('session_key')
        return session_key
    except Exception as e:
        logger.warning(
            f"Ошибка при получении session_key"
        )
        raise e
    

def get_results(session_key):
    try:
        response = urlopen(f'https://api.openf1.org/v1/session_result?'
                           f'session_key={session_key}&position%3C=22')
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        logger.warning(
            f"Ошибка при получении session_key"
        )
        raise e
    

def get_driver(session_key):
    try:
        response = urlopen(f"https://api.openf1.org/v1/drivers?"
                           f"session_key={session_key}")
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        logger.warning(
            f"Ошибка при получении session_key"
        )
        raise e


def get_sessions(session_key):
    try:
        results = get_results(session_key)
        return results
    except Exception as e:
        logger.warning(
            f"Ошибка при загрузке session_key из OpenF1"
        )
        raise e
    

def get_championship_drivers(session_key):
    try:
        response = urlopen(f"https://api.openf1.org/v1/championship_drivers?"
                           f"session_key={session_key}")
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        logger.warning(
            f"Ошибка при загрузке турнирной таблицы пилотов из OpenF1"
        )
        raise e
    

def get_championship_teams(session_key):
    try:
        response = urlopen(f"https://api.openf1.org/v1/championship_teams?"
                           f"session_key={session_key}")
        data = json.loads(response.read().decode('utf-8'))
        return data
    except Exception as e:
        logger.warning(
            f"Ошибка при загрузке кубка конструкторов из OpenF1"
        )
        raise e
