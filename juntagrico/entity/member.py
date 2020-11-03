import hashlib

from django.contrib.auth.models import User
from django.db import models

from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel, notifiable
from juntagrico.lifecycle.member import check_member_consistency
from juntagrico.util.users import make_username


def q_joined_subscription():
    return Q(join_date__isnull=False) & Q(join_date__lte=timezone.now().date())


def q_left_subscription():
    return Q(leave_date__isnull=False) & Q(leave_date__lte=timezone.now().date())


class Member(JuntagricoBaseModel):
    '''
    Additional fields for Django's default user class.
    '''

    # user class is only used for logins, permissions, and other builtin django stuff
    # all user information should be stored in the Member model
    user = models.OneToOneField(
        User, related_name='member', on_delete=models.CASCADE)

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

    confirmed = models.BooleanField(_('E-Mail-Adresse bestätigt'), default=False)
    reachable_by_email = models.BooleanField(
        _('Kontaktierbar von der Job Seite aus'), default=False)

    canceled = models.BooleanField(_('gekündigt'), default=False)
    cancelation_date = models.DateField(
        _('Kündigüngsdatum'), null=True, blank=True)
    end_date = models.DateField(
        _('Enddatum'), null=True, blank=True)
    inactive = models.BooleanField(_('inaktiv'), default=False,
                                   help_text=_('Sperrt Login und entfernt von E-Mail-Listen'))
    notes = models.TextField(
        _('Notizen'), max_length=1000, blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))

    @property
    def active_shares(self):
        """ :return: shares that have been paid by member and not cancelled AND paid back yet
        """
        return self.share_set.filter(paid_date__isnull=False).filter(payback_date__isnull=True)

    @property
    def active_shares_count(self):
        return self.active_shares.count()

    @property
    def is_cooperation_member(self):
        return self.active_shares_count > 0

    @property
    def usable_shares(self):
        """ :return: shares that have been ordered (i.e. created) and not cancelled yet
        """
        return self.share_set.filter(cancelled_date__isnull=True)

    @property
    def usable_shares_count(self):
        return self.usable_shares.count()

    @property
    def subscription_future(self):
        sub_membership = self.subscriptionmembership_set.filter(~q_joined_subscription()).first()
        return getattr(sub_membership, 'subscription', None)

    @property
    def subscription_current(self):
        sub_membership = self.subscriptionmembership_set.filter(q_joined_subscription() & ~q_left_subscription()).first()
        return getattr(sub_membership, 'subscription', None)

    @property
    def subscriptions_old(self):
        return [sm.subscription for sm in
                self.subscriptionmembership_set.filter(q_left_subscription())]

    def join_subscription(self, subscription):
        sub_membership = self.subscriptionmembership_set.filter(subscription=subscription).first()
        if sub_membership and sub_membership.leave_date:
            sub_membership.leave_date = None
            sub_membership.save()
        else:
            join_date = timezone.now().date() if subscription.active else None
            SubscriptionMembership.objects.create(member=self, subscription=subscription, join_date=join_date)

    def leave_subscription(self, subscription):
        sub_membership = self.subscriptionmembership_set.filter(subscription=subscription).first()
        membership_present = sub_membership and sub_membership.leave_date is None
        if membership_present and sub_membership.join_date is not None:
            sub_membership.leave_date = timezone.now().date()
            sub_membership.save()
        elif membership_present and sub_membership.join_date is None:
            sub_membership.delete()

    @property
    def in_subscription(self):
        return (self.subscription_future is not None) | (self.subscription_current is not None)

    @property
    def blocked(self):
        future = self.subscription_future is not None
        current = self.subscription_current is not None and not self.subscription_current.canceled
        return future or current

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
    def create(cls, sender, instance, **kwds):
        '''
        Callback to create corresponding user when new member is created.
        '''
        if getattr(instance, 'user', None) is None:
            username = make_username(
                instance.first_name, instance.last_name, instance.email)
            user, created = User.objects.get_or_create(username=username)
            instance.user = user

    @classmethod
    def post_delete(cls, sender, instance, **kwds):
        instance.user.delete()

    @notifiable
    class Meta:
        verbose_name = Config.vocabulary('member')
        verbose_name_plural = Config.vocabulary('member_pl')
        permissions = (('can_filter_members', _('Benutzer kann {0} filtern').format(Config.vocabulary('member_pl'))),)


class SubscriptionMembership(JuntagricoBaseModel):
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE)
    join_date = models.DateField(_('Beitrittsdatum'), null=True, blank=True)
    leave_date = models.DateField(_('Austrittsdatum'), null=True, blank=True)

    class Meta:
        unique_together = ('member', 'subscription')
        verbose_name = _('{}-Mitgliedschaft').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{}-Mitgliedschaften').format(Config.vocabulary('subscription'))
