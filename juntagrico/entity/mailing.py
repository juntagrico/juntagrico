from django.db import models
from django.utils.translation import gettext as _

from juntagrico.entity import JuntagricoBaseModel


class MailTemplate(JuntagricoBaseModel):
    '''
    Mail template for rendering
    '''
    name = models.CharField(_('Name'), max_length=100, unique=True)
    template = models.TextField(_('Template'), default='')
    code = models.TextField(_('Code'), default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('MailTemplate')
        verbose_name_plural = _('MailTemplates')
        permissions = (('can_load_templates', _(
            'Benutzer kann Templates laden')),)
