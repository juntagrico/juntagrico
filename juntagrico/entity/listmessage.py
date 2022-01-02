from django.db import models
from django.utils.translation import gettext as _

from juntagrico.entity import JuntagricoBaseModel


class ListMessage(JuntagricoBaseModel):
    '''
    Message to display at the bottom of the depot list
    '''
    message = models.CharField(_('Nachricht'), max_length=256)
    active = models.BooleanField(_('aktiv'), default=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = _('Depot Listen Nachricht')
        verbose_name_plural = _('Depot Listen Nachrichten')
        ordering = ['sort_order']
