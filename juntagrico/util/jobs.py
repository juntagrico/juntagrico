import math

from django.utils.translation import gettext as _


def get_status_image(percent=0):
    status_number = min(100, int(25 * math.floor(float(percent) / 25)))
    result = 'status_' + str(status_number)
    return result


def get_status_image_text(percent=0):
    texts = {
        100: _('Fertig'),
        75: _('Dreiviertel'),
        50: _('Halb'),
        25: _('Angefangen'),
        0: _('Nix')
    }
    status_number = min(100, int(25 * math.floor(float(percent) / 25)))
    return texts[status_number]
