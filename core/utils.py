from tz_detect.utils import offset_to_timezone


def get_timezone(tz):
    try:
        timezone = offset_to_timezone(tz)
        return timezone
    except TypeError:
        return tz
