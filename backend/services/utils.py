from datetime import timedelta
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from loguru import logger
from asgiref.sync import sync_to_async


geolocator = Nominatim(user_agent="f1_service")
tf = TimezoneFinder()


GP_FLAGS = {
    "Australian Grand Prix": "🇦🇺",
    "Chinese Grand Prix": "🇨🇳",
    "Japanese Grand Prix": "🇯🇵",
    "Bahrain Grand Prix": "🇧🇭",
    "Saudi Arabian Grand Prix": "🇸🇦",
    "Miami Grand Prix": "🇺🇸",
    "Canadian Grand Prix": "🇨🇦",
    "Monaco Grand Prix": "🇲🇨",
    "Barcelona Grand Prix": "🇪🇸",
    "Austrian Grand Prix": "🇦🇹",
    "British Grand Prix": "🇬🇧",
    "Belgian Grand Prix": "🇧🇪",
    "Hungarian Grand Prix": "🇭🇺",
    "Dutch Grand Prix": "🇳🇱",
    "Italian Grand Prix": "🇮🇹",
    "Spanish Grand Prix": "🇪🇸",
    "Azerbaijan Grand Prix": "🇦🇿",
    "Singapore Grand Prix": "🇸🇬",
    "United States Grand Prix": "🇺🇸",
    "Mexico City Grand Prix": "🇲🇽",
    "São Paulo Grand Prix": "🇧🇷",
    "Las Vegas Grand Prix": "🇺🇸",
    "Qatar Grand Prix": "🇶🇦",
    "Abu Dhabi Grand Prix": "🇦🇪",
}


DRIVER_FLAGS = {
    "NOR": "🇬🇧",
    "PIA": "🇦🇺",
    "VER": "🇳🇱",
    "HAD": "🇫🇷",
    "RUS": "🇬🇧",
    "ANT": "🇮🇹", 
    "HAM": "🇬🇧",
    "LEC": "🇲🇨",
    "SAI": "🇪🇸",
    "ALB": "🇹🇭",
    "LAW": "🇳🇿",
    "LIN": "🇬🇧",
    "ALO": "🇪🇸",
    "STR": "🇨🇦",
    "OCO": "🇫🇷",
    "BEA": "🇬🇧",
    "HUL": "🇩🇪",
    "BOR": "🇧🇷",
    "GAS": "🇫🇷",
    "COL": "🇦🇷",
    "PER": "🇲🇽",
    "BOT": "🇫🇮",
    "VES": "🇩🇰",
    "FOR": "🇮🇹",
    "HIR": "🇯🇵",
    "ARO": "🇪🇪",
    "HER": "🇺🇸",    
}


TEAMS_FLAGS = {
    "Mercedes": "🇩🇪",
    "Ferrari": "🇮🇹",
    "Red Bull": "🇦🇹",
    "McLaren": "🇬🇧",
    "Aston Martin": "🇬🇧",
    "Alpine": "🇫🇷",
    "Haas": "🇺🇸",
    "Williams": "🇬🇧",
    "Audi": "🇩🇪",
    "Racing Bulls": "🇮🇹",
    "Cadillac": "🇺🇸",
}


TEAMS_DISPLAY_NAMES = {
    "Red Bull Racing": "Red Bull",
    "Haas F1 Team": "Haas",
}


SESSION_MAP = {
    "fp1": "Practice 1",
    "fp2": "Practice 2",
    "fp3": "Practice 3",
    "sprint_qualifying": "Sprint Qualifying",
    "sprint": "Sprint",
    "qualifying": "Qualifying",
    "race": "Race"
}


PRACTICE_SESSIONS = [
    "fp1",
    "fp2",
    "fp3"
]


async def get_timezone_by_city(city):
    """
    Получение часового пояса по городу
    """
    city = city.strip().lower()
    try:
        location = await sync_to_async(geolocator.geocode)(city)
        if not location:
            return None
        
        user_tz = tf.timezone_at(
            lng=location.longitude,
            lat=location.latitude
        )

        return user_tz
    except Exception as e:
        logger.exception(f'Ошибка при получении часового пояса для города {city}: {e}')
        return None
    

def format_date(date):
    """
    Форматирует диапазон дат для отображения в календаре гонок
    """
    month_map = {
        'Jan': 'янв', 'Feb': 'фев', 'Mar': 'мар', 'Apr': 'апр',
        'May': 'май', 'Jun': 'июн', 'Jul': 'июл', 'Aug': 'авг',
        'Sep': 'сен', 'Oct': 'окт', 'Nov': 'ноя', 'Dec': 'дек'
    }
    start = date - timedelta(days=2)
    start_date = f"{start.day} {month_map.get(start.strftime('%b'), start.strftime('%b'))}"
    end_date = f"{date.day} {month_map.get(date.strftime('%b'), date.strftime('%b'))}"
    return f"{start_date} - {end_date}"