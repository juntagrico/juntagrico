from datetime import datetime


def date_from_get(request, name, default=None, date_format="%Y-%m-%d"):
    date = request.GET.get(name, None)
    if date is not None:
        return datetime.strptime(date, date_format).date()
    return default
