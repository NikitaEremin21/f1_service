from datetime import timedelta
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from loguru import logger


geolocator = Nominatim(user_agent="f1_service")
tf = TimezoneFinder()


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