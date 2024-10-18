from django import template
from django.utils.formats import number_format
from datetime import timedelta

register = template.Library()

@register.filter
def rate_star(rate):
    # Round the rate to the nearest 0.5 and convert to int if needed
    average_rate = round(rate * 2) / 2
    if average_rate % 1 == 0:
        return int(average_rate)
    return average_rate

@register.filter
def int_with_commas(value):
    try:
        if value is not None:
            return number_format(value, decimal_pos=0, use_l10n=True)
    except (ValueError, TypeError):
        return value  # Return the original value if conversion fails
    return value

@register.filter
def get_days_until(start_date, end_date):
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

@register.filter
def date_add(date_obj, days):
    return date_obj + timedelta(days=days)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)

@register.filter
def get_reservation(reservations, date_time):
    date, time = date_time.split()
    date = date.strip()
    time = time.strip()
    for reservation in reservations:
        if str(reservation.date) == date and str(reservation.time_start) == time:
            return reservation
    return None