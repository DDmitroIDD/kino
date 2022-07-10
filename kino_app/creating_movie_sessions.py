import json
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db.models import Q


def create_dates(data, hall):
    start_date = data.get('start_datetime', False)
    end_date = data.get('end_datetime', False)
    time_range = datetime.combine(start_date.date(), end_date.time()) - \
                 datetime.combine(start_date.date(), start_date.time())

    day_range = end_date.date() - start_date.date()

    dates = [(start_date + timedelta(days=day), start_date + timedelta(days=day, seconds=time_range.seconds))
             for day in range(day_range.days + 1)]

    for start, end in dates:
        if hall and hall.filter(Q(
                start_datetime__range=(start, end)) | Q(end_datetime__range=(start, end))):
            raise ValidationError({'movie_sessions_error': 'There is movie no this time in this hall!'})
    return dates
