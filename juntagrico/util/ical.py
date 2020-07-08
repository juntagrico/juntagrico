import re
from collections import namedtuple

from django.utils import timezone
from django.utils.translation import gettext as _
from ics import Calendar, Event
from ics.parse import ContentLine

from juntagrico.config import Config

'''
    Create a ical string from an job
'''


ical = namedtuple("ical", ["name", "content"])


def generate_ical_for_job(job):
    # Used https://icalendar.org/validator.html to validate output
    # Gmail will not update or cancel the existing event, but add a new one if the method is PUBLISH,
    # However, using REQUEST as the method would cause more confusion as it would look to the members as if they could
    # actually cancel their participation, be declining the event.
    # Thunderbird recognizes the changes correctly
    # On Android Gmail will show the same behaviour as on the desktop when using the event widget. Opening the attached
    # ics with a Calender App (e.g. Google Calendar) yields the correct behaviour (existing event is overwritten).
    # Using a non Gmail account in the Gmail app seems to break the ics file, for some reason.
    # K9-Mail shows the attachment and opening it in a calendar app works fine.
    # Outlook and Microsoft Mail do not show the event nicely, however the ics attachment can be opened and added to
    # calendar.
    # Not tested yet: Apples
    c = Calendar()
    c.extra.append(ContentLine(name="METHOD", value="CANCEL" if job.canceled else "PUBLISH"))
    e = Event()
    # By giving it a UID the calendar will (hopefully) replace previous versions of this event.
    e.uid = f'{repr(job)}@{Config.server_url()}'
    # DTSTAMP is required: https://tools.ietf.org/html/rfc5545#section-3.6.1
    e.extra.append(ContentLine(name="DTSTAMP",
                               value=timezone.now().astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')))
    e.name = Config.organisation_name() + ' ' + _('Einsatz') + ': ' + job.type.get_name
    e.location = job.type.location
    e.description = job.type.description
    # Using FORM 2: https://tools.ietf.org/html/rfc5545#section-3.3.5
    e.begin = job.start_time()
    e.duration = {'hours': job.duration}
    e.extra.append(ContentLine(name=f"ORGANIZER;CN={Config.organisation_name()}",
                               value=f"mailto:{job.type.activityarea.get_email()}"))
    if job.canceled:
        e.status = 'CANCELLED'
    c.events.add(e)
    content = re.sub(r"\r?\n", "\r\n", str(c))
    # Fold lines https://tools.ietf.org/html/rfc5545#section-3.1
    content = re.sub("(.{74})", "\\1\r\n ", content)  # fold at 74 such that the whitespace fits
    return ical("{}.ics".format(_('Einsatz')), content)
