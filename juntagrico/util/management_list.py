from juntagrico.view_decorators import using_change_date


@using_change_date
def get_changedate(request, change_date, default=None):
    can_change_date = change_date is None
    return {'change_date': change_date or default,
            'can_change_date': can_change_date}
