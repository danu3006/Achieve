from django.utils.timezone import localtime, now

from . import models


def get_current_quarter():
    quarters = models.Quarter.objects.all()
    this_current_quarter = None

    for quarter in quarters:
        if quarter.start_date <= localtime(now()).date() <= quarter.end_date:
            this_current_quarter = quarter

    return this_current_quarter


def current_quarter(request):
    return {
        'current_quarter': get_current_quarter(),
    }
