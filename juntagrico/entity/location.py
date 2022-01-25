from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
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
    visible = models.BooleanField(_('Sichtbar'), default=True,
                                  help_text=_('Ort steht bei Einsatz und {} zur Auswahl').format(
                                      Config.vocabulary('depot')))
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    @property
    def has_coordinates(self):
        lat = self.latitude is not None and self.latitude != ''
        long = self.longitude is not None and self.longitude != ''
        return lat and long

    @property
    def has_geo(self):
        street = self.addr_street is not None and self.addr_street != ''
        zipcode = self.addr_zipcode is not None and self.addr_zipcode != ''
        loc = self.addr_location is not None and self.addr_location != ''
        return self.has_coordinates and street and zipcode and loc

    @property
    def map_info(self):
        return {
            "name": self.name,
            "addr_street": self.addr_street,
            "addr_zipcode": self.addr_zipcode,
            "addr_location": self.addr_location,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    @property
    def google_maps_query(self):
        if self.longitude is not None and self.latitude is not None:
            return '{},{}'.format(self.latitude, self.longitude)
        return self.address

    @property
    def city(self):
        return '{} {}'.format(self.addr_zipcode or '', self.addr_location or '').strip()

    def get_address(self):
        return [a for a in [self.addr_street, self.city] if a]

    @property
    def address(self):
        return ', '.join(self.get_address())

    @property
    def address_html(self):
        return '<br>'.join(self.get_address())

    @property
    def to_html(self):
        return '<br>'.join([self.name, *self.get_address()])

    def __str__(self):
        string = str(self.name)
        if address := self.address:
            return string + ', ' + address
        return string

    class Meta:
        verbose_name = _('Ort')
        verbose_name_plural = _('Orte')
        ordering = ['sort_order']
