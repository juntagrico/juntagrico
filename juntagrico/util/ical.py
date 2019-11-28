from ics import Calendar, Event

from django.utils.translation import gettext as _

from juntagrico.config import Config

'''
    Create a ical string from an job
'''


def generate_ical_for_job(job):
    c = Calendar()
    e = Event()
    e.name = Config.organisation_name() + ' ' + _('Einsatz') + ':' + job.type.get_name
    e.location = job.type.location
    e.description = job.type.description
    e.begin = job.time.strftime('%Y%m%d %H:%M:%S')
    e.end = job.time.strftime('%Y%m%d %H:%M:%S')
    # c.events.append(e)
    return str(c).replace('\n', '\r\n') + '\r\n'
