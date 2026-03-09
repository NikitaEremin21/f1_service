from datetime import timedelta
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from loguru import logger


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
    "Barcelona‑Catalunya Grand Prix": "🇪🇸",
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
}


def get_timezone_by_city(city):
    city = city.strip().lower()
    try:
        location = geolocator.geocode(city)
        if not location:
            return None
        
        user_tz = tf.timezone_at(
            lng=location.longitude,
            lat=location.latitude
        )

        return user_tz
    except Exception as e:
        logger.error(f'Ошибка при получении часового пояса для города {city}: {e}')
        return None
    

def format_date(date):
    month_map = {
        'Jan': 'янв', 'Feb': 'фев', 'Mar': 'мар', 'Apr': 'апр',
        'May': 'май', 'Jun': 'июн', 'Jul': 'июл', 'Aug': 'авг',
        'Sep': 'сен', 'Oct': 'окт', 'Nov': 'ноя', 'Dec': 'дек'
    }
    start = date - timedelta(days=2)
    start_date = f"{start.day} {month_map.get(start.strftime('%b'), start.strftime('%b'))}"
    end_date = f"{date.day} {month_map.get(date.strftime('%b'), date.strftime('%b'))}"
    return f"{start_date} - {end_date}"