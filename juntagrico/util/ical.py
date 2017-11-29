from ics import Calendar, Event

from juntagrico.config import *

'''
    Create a ical string from an job
'''


def genecrate_ical_for_job(job):
    c = Calendar()
    e = Event()
    e.name = Config.organisation_name() + ' Einsatz:' + job.type.name
    e.location = job.type.location
    e.description = job.type.description
    e.begin = job.time.strftime('%Y%m%d %H:%M:%S')
    e.end = job.time.strftime('%Y%m%d %H:%M:%S')
    c.events.append(e)
    return str(c).replace('\n', '\r\n') + '\r\n'
