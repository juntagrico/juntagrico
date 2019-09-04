from django.db import models
from django.utils.translation import gettext as _

from juntagrico.entity import JuntagricoBaseModel


class ListMessage(JuntagricoBaseModel):
    '''
    Message to display at the bottom of the depot list
    '''
    message = models.CharField(_('Nachricht'), max_length=256)
    active = models.BooleanField(_('aktiv'), default=True)
    sort_order = models.FloatField(_('Nummer zum Sortieren'), default=1.0)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = _('Depot Listen Nachricht')
        verbose_name_plural = _('Depot Listen Nachrichten')
