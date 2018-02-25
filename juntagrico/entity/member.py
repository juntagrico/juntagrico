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

    first_name = models.CharField('Vorname', max_length=30)
    last_name = models.CharField('Nachname', max_length=30)
    email = models.EmailField(unique=True)

    addr_street = models.CharField('Strasse', max_length=100)
    addr_zipcode = models.CharField('PLZ', max_length=10)
    addr_location = models.CharField('Ort', max_length=50)
    birthday = models.DateField('Geburtsdatum', null=True, blank=True)
    phone = models.CharField('Telefonnr', max_length=50)
    mobile_phone = models.CharField('Mobile', max_length=50, null=True, blank=True)
    
    iban = models.CharField('IBAN', max_length=100, blank=True, default='')

    future_subscription = models.ForeignKey('Subscription', related_name='members_future', null=True, blank=True,
                                     on_delete=models.SET_NULL)
    subscription = models.ForeignKey('Subscription', related_name='members', null=True, blank=True,
                                     on_delete=models.SET_NULL)
    old_subscriptions = models.ManyToManyField('Subscription', related_name='members_old')

    confirmed = models.BooleanField('bestätigt', default=False)
    reachable_by_email = models.BooleanField('Kontaktierbar von der Job Seite aus', default=False)
    
    canceled = models.BooleanField('gekündigt', default=False)
    cancelation_date = models.DateField('Kündigüngssdatum', null=True, blank=True)
    inactive = models.BooleanField('inaktiv', default=False)

          
    @property
    def is_cooperation_member(self):
        return self.share_set.filter(paid_date__isnull=False).filter(
            payback_date__isnull=True).count()>0
    
    @property
    def active_shares(self):
        return self.share_set.filter(
            cancelled_date__isnull=True)
            
    @property
    def active_shares_count(self):
        return self.active_shares.count()
            
    @property
    def blocked(self):
        future = self.future_subscription is not None
        current = self.subscription is None or not self.subscription.canceled
        return future or not current 

        
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
        if instance.inactive is True:
            instance.areas = ()

    class Meta:
        verbose_name = Config.member_string()
        verbose_name_plural = Config.members_string()
        permissions = (('can_filter_members', 'Benutzer kann ' + Config.members_string() + ' filtern'),)

    def get_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_phone(self):
        if self.mobile_phone != '':
            return self.mobile_phone
        return self.phone
