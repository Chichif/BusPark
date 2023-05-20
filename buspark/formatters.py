from datetime import timedelta

def timedelta_to_str(time_difference: timedelta) -> str:
    '''
    Перетворює об'єкт datetime.timedelta у строку у форматі ГГ:ХХ:СС.
    Повертає: str
    '''
    hours = time_difference.total_seconds() // 3600
    minutes = (time_difference.total_seconds() // 60) % 60
    seconds = time_difference.total_seconds() % 60
    time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    return time_str