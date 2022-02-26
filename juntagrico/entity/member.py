import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel, notifiable, LowercaseEmailField
from juntagrico.lifecycle.member import check_member_consistency
from juntagrico.lifecycle.submembership import check_sub_membership_consistency
from juntagrico.queryset.member import MemberQuerySet
from juntagrico.util.users import make_username


def q_joined_subscription():
    return Q(join_date__isnull=False, join_date__lte=timezone.now().date())


def q_left_subscription(asof=None):
    asof = asof or timezone.now().date()
    return Q(leave_date__isnull=False, leave_date__lte=asof)


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
    email = LowercaseEmailField(unique=True)

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
    cancellation_date = models.DateField(
        _('Kündigungsdatum'), null=True, blank=True)
    deactivation_date = models.DateField(
        _('Deaktivierungsdatum'), null=True, blank=True, help_text=_('Sperrt Login und entfernt von E-Mail-Listen'))
    end_date = models.DateField(
        _('Enddatum'), null=True, blank=True, help_text=_('Voraususchtliches Datum an dem die Mitgliedschaft enden wird. Hat keinen Effekt im System'))
    notes = models.TextField(
        _('Notizen'), max_length=1000, blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))
    number = models.IntegerField(_('Mitglieder-Nummer'), null=True, blank=True)
    subscription = models.ManyToManyField('Subscription', through='SubscriptionMembership', related_name='members')

    objects = MemberQuerySet.as_manager()

    @property
    def canceled(self):
        return self.cancellation_date is not None and self.cancellation_date <= timezone.now().date()

    @property
    def inactive(self):
        return self.deactivation_date is not None and self.deactivation_date <= timezone.now().date()

    @property
    def is_cooperation_member(self):
        return self.shares.active().count() > 0

    @property
    def required_shares_count(self):
        # calculate required shares backwards to account for shared subscriptions
        not_canceled_share_count = self.shares.usable().count()
        overflow_list = [not_canceled_share_count]
        if self.subscription_future is not None:
            overflow_list.append(self.subscription_future.share_overflow)
        if self.subscription_current is not None:
            overflow_list.append(self.subscription_current.share_overflow)
        return not_canceled_share_count - min(overflow_list)

    @property
    def cancellable_shares_count(self):
        return self.shares.usable().count() - max(self.required_shares_count, 1)

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
            join_date = None if subscription.waiting else timezone.now().date()
            SubscriptionMembership.objects.create(member=self, subscription=subscription, join_date=join_date)

    def leave_subscription(self, subscription, changedate=None):
        sub_membership = self.subscriptionmembership_set.filter(subscription=subscription).first()
        membership_present = sub_membership and sub_membership.leave_date is None
        if membership_present and sub_membership.join_date is not None:
            changedate = changedate or timezone.now().date()
            sub_membership.leave_date = changedate
            sub_membership.save()
        elif membership_present and sub_membership.join_date is None:
            sub_membership.delete()

    @property
    def in_subscription(self):
        return (self.subscription_future is not None) | (self.subscription_current is not None)

    @property
    def can_order_subscription(self):
        return self.subscription_future is None and (
            self.subscription_current is None or self.subscription_current.cancellation_date is not None)

    @property
    def blocked(self):
        future = self.subscription_future is not None
        current = self.subscription_current is not None and not self.subscription_current.inactive
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
                instance.first_name, instance.last_name)
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

    def clean(self):
        return check_sub_membership_consistency(self)

    class Meta:
        unique_together = ('member', 'subscription')
        verbose_name = _('{}-Mitgliedschaft').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{}-Mitgliedschaften').format(Config.vocabulary('subscription'))
