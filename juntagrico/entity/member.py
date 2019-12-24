import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel, notifiable
from juntagrico.lifecycle.member import check_member_consistency
from juntagrico.util.users import make_username


class Member(JuntagricoBaseModel):
    '''
    Additional fields for Django's default user class.
    '''

    # user class is only used for logins, permissions, and other builtin django stuff
    # all user information should be stored in the Member model
    user = models.OneToOneField(
        User, related_name='member', null=True, blank=True, on_delete=models.CASCADE)

    first_name = models.CharField(_('Vorname'), max_length=30)
    last_name = models.CharField(_('Nachname'), max_length=30)
    email = models.EmailField(unique=True)

    addr_street = models.CharField(_('Strasse'), max_length=100)
    addr_zipcode = models.CharField(_('PLZ'), max_length=10)
    addr_location = models.CharField(_('Ort'), max_length=50)
    birthday = models.DateField(_('Geburtsdatum'), null=True, blank=True)
    phone = models.CharField(_('Telefonnr'), max_length=50)
    mobile_phone = models.CharField(
        _('Mobile'), max_length=50, null=True, blank=True)

    iban = models.CharField('IBAN', max_length=100, blank=True, default='')

    future_subscription = models.ForeignKey('Subscription', related_name='members_future', null=True, blank=True,
                                            on_delete=models.SET_NULL)
    subscription = models.ForeignKey('Subscription', related_name='members', null=True, blank=True,
                                     on_delete=models.SET_NULL)
    old_subscriptions = models.ManyToManyField(
        'Subscription', related_name='members_old')

    confirmed = models.BooleanField(_('bestätigt'), default=False)
    reachable_by_email = models.BooleanField(
        _('Kontaktierbar von der Job Seite aus'), default=False)

    canceled = models.BooleanField(_('gekündigt'), default=False)
    cancelation_date = models.DateField(
        _('Kündigüngsdatum'), null=True, blank=True)
    end_date = models.DateField(
        _('Enddatum'), null=True, blank=True)
    inactive = models.BooleanField(_('inaktiv'), default=False)
    notes = models.TextField(_('Notizen'), max_length=1000, blank=True)

    @property
    def is_cooperation_member(self):
        return self.share_set.filter(paid_date__isnull=False).filter(
            payback_date__isnull=True).count() > 0

    @property
    def active_shares(self):
        return self.share_set.filter(cancelled_date__isnull=True)

    @property
    def active_shares_count(self):
        return self.active_shares.count()

    @property
    def in_subscription(self):
        return (self.future_subscription is not None) | (self.subscription is not None)

    @property
    def blocked(self):
        future = self.future_subscription is not None
        current = self.subscription is None or not self.subscription.canceled
        return future or not current

    def get_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_phone(self):
        if self.mobile_phone != '':
            return self.mobile_phone
        return self.phone

    def get_hash(self):
        return hashlib.sha1((str(self.email) + str(self.pk)).encode('utf8')).hexdigest()

    def __str__(self):
        return self.get_name()

    def clean(self):
        check_member_consistency(self)

    @classmethod
    def create(cls, sender, instance, created, **kwds):
        '''
        Callback to create corresponding user when new member is created.
        '''
        if created and instance.user is None:
            username = make_username(
                instance.first_name, instance.last_name, instance.email)
            user = User(username=username)
            user.save()
            user = User.objects.get(username=username)
            instance.user = user
            instance.save()

    @classmethod
    def post_delete(cls, sender, instance, **kwds):
        instance.user.delete()

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('member')
        verbose_name_plural = Config.vocabulary('member_pl')
        permissions = (('can_filter_members', _('Benutzer kann {0} filtern').format(Config.vocabulary('member_pl'))),)
