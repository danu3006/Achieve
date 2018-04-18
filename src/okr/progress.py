from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from .models import (Result)


def update_progress(request, kr_id, type):
    result = get_object_or_404(Result, pk=kr_id)
    percentage = int(result.percentage)
    if request.user == result.objective.user:
        if type == "increase":
            if percentage == 0:
                result.percentage = 50
            elif percentage == 50:
                result.percentage = 75
            elif percentage == 75:
                result.percentage = 100
            elif percentage == 100:
                messages.error(request, 'ERROR: Progress already at highest (100%)!')

        elif type == "decrease":
            if percentage == 0:
                messages.error(request, 'ERROR: Progress already at lowest (0%)!')
            elif percentage == 50:
                result.percentage = 0
            elif percentage == 75:
                result.percentage = 50
            elif percentage == 100:
                result.percentage = 75

    result.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
