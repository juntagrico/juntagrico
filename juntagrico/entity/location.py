from django.db import models
from django.utils.translation import gettext as _

from juntagrico.entity import JuntagricoBaseModel


class Location(JuntagricoBaseModel):
    """
    Location information
    """
    name = models.CharField(_('Name'), max_length=100, unique=True)
    latitude = models.DecimalField(_('Breitengrad'), max_length=100,
                                   null=True, blank=True, max_digits=9, decimal_places=6)
    longitude = models.DecimalField(_('Längengrad'), max_length=100,
                                    null=True, blank=True, max_digits=9, decimal_places=6)
    addr_street = models.CharField(_('Strasse & Nr.'), max_length=100,
                                   null=True, blank=True)
    addr_zipcode = models.CharField(_('PLZ'), max_length=10,
                                    null=True, blank=True)
    addr_location = models.CharField(_('Ort'), max_length=50,
                                     null=True, blank=True)
    description = models.TextField(_('Beschreibung'), max_length=1000, default='', blank=True)
    visible = models.BooleanField(_('Sichtbar'), default=True)
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    @property
    def google_maps_query(self):
        if self.longitude is not None and self.latitude is not None:
            return '{},{}'.format(self.latitude, self.longitude)
        return self.address

    @property
    def address(self):
        return '{}, {} {}'.format(self.addr_street or '', self.addr_zipcode or '', self.addr_location or '').strip(', ')

    def __str__(self):
        string = str(self.name)
        if address := self.address:
            return string + ', ' + address
        return string

    class Meta:
        verbose_name = _('Ort')
        verbose_name_plural = _('Orte')
        ordering = ['sort_order']
