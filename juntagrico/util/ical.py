from collections import namedtuple
from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext as _
from icalendar import Calendar, Event, vDatetime

from juntagrico.config import Config

'''
    Create a ical string from an job
'''


ical = namedtuple("ical", ["name", "content"])


def generate_ical_for_job(job):
    c = Calendar()
    c.add(name='METHOD', value='CANCEL' if job.canceled else 'PUBLISH')
    c.add(name='PRODID', value='juntagrico')
    c.add(name='VERSION', value='2.0')
    e = Event()
    # By giving it a UID the calendar will (hopefully) replace previous versions of this event.
    e.add(name='UID', value=f'{repr(job)}@{Config.server_url()}')
    e['DTSTAMP'] = vDatetime(timezone.now()).to_ical()
    e.add(name='NAME', value=Config.organisation_name() + ' ' + _('Einsatz') + ': ' + job.type.get_name)
    e.add(name='LOCATION', value=job.type.location)
    e.add(name='DESCRIPTION', value=job.type.description)
    e['DTSTART'] = vDatetime(job.start_time()).to_ical()
    e.add(name='DURATION', value=timedelta(hours=job.duration))
    e.add(name=f"ORGANIZER;CN={Config.organisation_name()}",
          value=f"mailto:{job.type.activityarea.get_email()}")
    if job.canceled:
        e.add(name='STATUS', value='CANCELLED')
    c.add_component(e)
    content = c.to_ical()
    return ical("{}.ics".format(_('Einsatz')), content)
