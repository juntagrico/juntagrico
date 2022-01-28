from pathlib import Path

from django.db import models
from django.template.loader import get_template
from django.utils.translation import gettext as _

from juntagrico.entity import JuntagricoBaseModel


def get_overridable_templates():
    """ collets the overridable templates from the textsnippets folder
    :return: an iterable of tuples with the relative paths to overridable text templates and its file name
    """
    local_templates = Path(__file__).parent.parent / 'templates'
    text_templates = local_templates / 'textsnippets'
    for path in text_templates.glob('*'):
        yield path.relative_to(local_templates).as_posix(), path.relative_to(text_templates).as_posix()


class TextOverride(JuntagricoBaseModel):
    """
    Template text overrides
    """
    name = models.CharField(_('Name'), max_length=100, unique=True, choices=get_overridable_templates())
    text = models.TextField(_('Text'), max_length=3000, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Textanpassung')
        verbose_name_plural = _('Textanpassungen')


def pre_save(sender, instance, **kwds):
    """ on creation the overridden text is populated with the default text
    """
    if not instance.pk:
        instance.text = get_template(instance.name).template.source
