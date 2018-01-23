# encoding: utf-8

from django.db import models
from django.contrib.auth.models import User

from juntagrico.util.users import *
from juntagrico.config import Config

class Member(models.Model):
    '''
    Additional fields for Django's default user class.
    '''

    # user class is only used for logins, permissions, and other builtin django stuff
    # all user information should be stored in the Member model
    user = models.OneToOneField(User, related_name='member', null=True, blank=True, on_delete=models.CASCADE)

    first_name = models.CharField(_('Vorname'), max_length=30)
    last_name = models.CharField(_('Nachname'), max_length=30)
    email = models.EmailField(unique=True)

    addr_street = models.CharField(_('Strasse'), max_length=100)
    addr_zipcode = models.CharField(_('PLZ'), max_length=10)
    addr_location = models.CharField(_('Ort'), max_length=50)
    birthday = models.DateField(_('Geburtsdatum'), null=True, blank=True)
    phone = models.CharField(_('Telefonnr'), max_length=50)
    mobile_phone = models.CharField(_('Mobile'), max_length=50, null=True, blank=True)

    subscription = models.ForeignKey('Subscription', related_name='members', null=True, blank=True,
                                     on_delete=models.SET_NULL)

    confirmed = models.BooleanField(_('bestätigt'), default=False)
    reachable_by_email = models.BooleanField(_('Kontaktierbar von der Job Seite aus'), default=False)
    block_emails = models.BooleanField(_('keine emails'), default=False)

    old_subscription = None

    def __str__(self):
        return self.get_name()

    @classmethod
    def create(cls, sender, instance, created, **kwds):
        '''
        Callback to create corresponding member when new user is created.
        '''
        if created and instance.user is None:
            username = make_username(instance.first_name, instance.last_name, instance.email)
            user = User(username=username)
            user.save()
            user = User.objects.get(username=username)
            instance.user = user
            instance.save()

    @classmethod
    def post_delete(cls, sender, instance, **kwds):
        instance.user.delete()

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        if instance.old_subscription != instance.subscription and instance.subscription is None:
            instance.areas = ()

    @classmethod
    def post_init(cls, sender, instance, **kwds):
        instance.old_subscription = None  # instance.subscription

    class Meta:
        verbose_name = Config.member_string()
        verbose_name_plural = Config.members_string()
        permissions = (('can_filter_members', _('Benutzer kann ') + Config.members_string() + _(' filtern')),)

    def get_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_phone(self):
        if self.mobile_phone != '':
            return self.mobile_phone
        return self.phone