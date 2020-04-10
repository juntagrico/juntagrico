from django.utils.translation import gettext as _

from juntagrico.config import Config

"""
    c means case
"""


def enriched_organisation(c):
    g = Config.organisation_name_config()['gender'].upper()
    if (c == 'N' and g == 'M') or ((c == 'G' or c == 'D') and g == 'F'):
        article = _('der')
    elif c == 'G' and (g == 'M' or g == 'N'):
        article = _('des')
    elif c == 'D' and (g == 'M' or g == 'N'):
        article = _('dem')
    elif c == 'A' and g == 'M':
        article = _('den')
    elif (c == 'N' or c == 'A') and g == 'F':
        article = _('die')
    elif (c == 'N' or c == 'A') and g == 'N':
        article = _('des')
    else:
        article = ''

    name = article + ' ' + \
        Config.organisation_name_config(
        )['type'] + ' ' + Config.organisation_name()

    return name.strip()
