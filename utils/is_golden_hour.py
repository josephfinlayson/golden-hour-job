from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz


def is_golden_hour(date_now, sunset, sunrise):
    sunset_end_range = sunset + timedelta(minutes=30)
    sunset_begin_range = sunset - timedelta(minutes=30)

    sunrise_end_range = sunrise + timedelta(minutes=30)
    sunrise_begin_range = sunrise - timedelta(minutes=30)

    is_sunrise = sunrise_begin_range < date_now < sunrise_end_range
    is_sunset = sunset_begin_range < date_now < sunset_end_range
    return is_sunrise or is_sunset


def  get_dates():
    u = datetime.utcnow()
    # NOTE: it works only with a fixed utc offset
    now = u.replace(tzinfo=pytz.utc)

    city = LocationInfo("Berlin", "Germany", "Europe/Berlin", 52.52, 13.4050)
    s = sun(city.observer, date=now)
    is_golden = is_golden_hour(now,  s['sunrise'], s['sunset'])