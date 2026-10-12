import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from juntagrico.view_decorators import using_change_date

CHANGE_DATE_PARAMETER = 'changedate'


@using_change_date
def get_changedate(_, change_date, default=None):
    can_change_date = change_date is None
    return {'change_date': change_date or default,
            'can_change_date': can_change_date}


def store_change_date(request, date):
    """
    stores the change date in the session. Setting it to today resets it.
    """
    if date == datetime.date.today():
        request.session['changedate'] = None
    else:
        request.session['changedate'] = date.isoformat()


class ChangeDateFromUrlMixin:
    """
    View mixin
    Allows setting the change date once from outside with the GET parameter `changedate`, e.g. `?changedate=2026-11-01`.
    The date is stored in the session and the request is redirected to the url without the parameter.
    """
    def get(self, request, *args, **kwargs):
        if CHANGE_DATE_PARAMETER not in request.GET:
            return super().get(request, *args, **kwargs)
        try:
            store_change_date(request, datetime.date.fromisoformat(request.GET[CHANGE_DATE_PARAMETER]))
        except ValueError:
            messages.error(request, _('Bitte gib ein Datum im Format JJJJ-MM-TT ein.'))
        query = request.GET.copy()
        del query[CHANGE_DATE_PARAMETER]
        url = request.path
        if query:
            url += '?' + query.urlencode()
        return HttpResponseRedirect(url)
