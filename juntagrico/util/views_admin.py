from datetime import datetime

from django.shortcuts import render


def date_from_get(request, name, default=None, date_format="%Y-%m-%d"):
    date = request.GET.get(name, None)
    if date is not None:
        return datetime.strptime(date, date_format).date()
    year = request.GET.get(name + '_year', None)
    if year is not None:
        month = request.GET.get(name + '_month', 1)
        day = request.GET.get(name + '_day', 1)
        return datetime(int(year), int(month), int(day)).date()
    return default


def subscription_management_list(management_list, renderdict, template, request):
    renderdict.update({
        'management_list': management_list,
    })
    return render(request, template, renderdict)
