def get_changedate(request):
    change_date = request.session.get('changedate', None)
    can_change_date = change_date is None
    return {'change_date': change_date,
            'can_change_date': can_change_date}
