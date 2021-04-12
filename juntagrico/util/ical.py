import re
from collections import namedtuple
from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext as _
from icalendar import Calendar, Event

from juntagrico.config import Config

'''
    Create a ical string from an job
'''


ical = namedtuple("ical", ["name", "content"])


def generate_ical_for_job(job):
    c = Calendar()
    c.add(name='METHOD', value='CANCEL' if job.canceled else 'PUBLISH')
    e = Event()
    # By giving it a UID the calendar will (hopefully) replace previous versions of this event.
    e.add(name='UID', value=f'{repr(job)}@{Config.server_url()}')
    e.add(name='DTSTAMP', value=timezone.now())
    e.add(name='NAME', value=Config.organisation_name() + ' ' + _('Einsatz') + ': ' + job.type.get_name)
    e.add(name='LOCATION', value=job.type.location)
    e.add(name='DESCRIPTION', value=job.type.description)
    e.add(name='BEGIN', value=job.start_time())
    e.add(name='DURATION', value=timedelta(hours=job.duration))
    e.add(name=f"ORGANIZER;CN={Config.organisation_name()}",
                               value=f"mailto:{job.type.activityarea.get_email()}")
    if job.canceled:
        e.add(name='STATUS', value='CANCELLED')
    c.add_component(e)
    content = c.to_ical().decode()
    # Fold lines https://tools.ietf.org/html/rfc5545#section-3.1
    content = re.sub("(.{74})", "\\1\r\n ", content)  # fold at 74 such that the whitespace fits
    return ical("{}.ics".format(_('Einsatz')), content)
