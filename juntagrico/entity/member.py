import datetime
import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBaseModel, notifiable, LowercaseEmailField, validate_iban
from juntagrico.lifecycle.member import check_member_consistency
from juntagrico.lifecycle.submembership import check_sub_membership_consistency
from juntagrico.queryset.member import MemberQuerySet
from juntagrico.util.users import make_username


def q_joined_subscription():
    return Q(join_date__isnull=False, join_date__lte=datetime.date.today())


def q_left_subscription(asof=None):
    if asof is not None:
        return Q(leave_date__isnull=False, leave_date__lte=asof)
    return Q(leave_date__isnull=False, leave_date__lte=datetime.date.today())


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

    iban = models.CharField('IBAN', max_length=100, blank=True, default='', validators=[validate_iban])

    confirmed = models.BooleanField(_('E-Mail-Adresse bestätigt'), default=False)
    reachable_by_email = models.BooleanField(
        _('Kontaktierbar von der Job Seite aus'), default=False)
    cancellation_date = models.DateField(
        _('Kündigungsdatum'), null=True, blank=True)
    deactivation_date = models.DateField(
        _('Deaktivierungsdatum'), null=True, blank=True, help_text=_('Sperrt Login und entfernt von E-Mail-Listen'))
    end_date = models.DateField(
        _('Enddatum'), null=True, blank=True, help_text=_('Voraussichtliches Datum an dem die Mitgliedschaft enden wird. Hat keinen Effekt im System'))
    notes = models.TextField(
        _('Notizen'), blank=True,
        help_text=_('Notizen für Administration. Nicht sichtbar für {}'.format(Config.vocabulary('member'))))
    number = models.IntegerField(_('Mitglieder-Nummer'), null=True, blank=True)

    objects = MemberQuerySet.as_manager()

    @property
    def canceled(self):
        return self.cancellation_date is not None and self.cancellation_date <= datetime.date.today()

    @property
    def inactive(self):
        return self.deactivation_date is not None and self.deactivation_date <= datetime.date.today()

    @property
    def active_shares(self):
        """ :return: shares that have been paid by member and not cancelled AND paid back yet
        """
        return self.share_set.active()

    def active_shares_for_date(self, date):
        date = date or datetime.date.today()
        return self.share_set.filter(paid_date__lte=date).filter(Q(payback_date__isnull=True) | Q(payback_date__gte=date))

    @property
    def active_share_years(self):
        """ :return: list of years spanning member's first to last active share in the past
        """
        shares = self.share_set.filter(paid_date__isnull=False).order_by('paid_date')
        years = []
        if shares:
            first_share_date = datetime.date.today()
            last_share_date = datetime.date.min
            for share in shares:
                first_share_date = min(first_share_date, share.paid_date)
                if share.payback_date:
                    last_share_date = max(last_share_date, share.payback_date)
                else:
                    last_share_date = datetime.date.today()
                last_share_date = max(last_share_date, first_share_date)
            years = list(range(first_share_date.year, last_share_date.year + 1))
            years = [y for y in years if y <= datetime.date.today().year]
        return years

    @property
    def active_shares_count(self):
        if self.pk is None:
            return 0
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
        if self.pk is None:
            return 0
        return self.usable_shares.count()

    @property
    def required_shares_count(self):
        # calculate required shares backwards to account for shared subscriptions
        not_canceled_share_count = self.usable_shares_count
        overflow_list = [not_canceled_share_count]
        if self.subscription_future is not None:
            overflow_list.append(self.subscription_future.share_overflow)
        if self.subscription_current is not None:
            overflow_list.append(self.subscription_current.share_overflow)
        return not_canceled_share_count - min(overflow_list)

    @property
    def cancellable_shares_count(self):
        return self.usable_shares_count - max(self.required_shares_count, 1)

    @property
    def subscription_future(self):
        sub_membership = self.subscriptionmembership_set.filter(~q_joined_subscription()).first()
        return getattr(sub_membership, 'subscription', None)

    @cached_property
    def subscription_current(self):
        sub_membership = self.subscriptionmembership_set.filter(q_joined_subscription() & ~q_left_subscription()).first()
        return getattr(sub_membership, 'subscription', None)

    @property
    def subscriptions_old(self):
        return [sm.subscription for sm in
                self.subscriptionmembership_set.filter(q_left_subscription())]

    def join_subscription(self, subscription, primary=False):
        sub_membership = self.subscriptionmembership_set.filter(subscription=subscription).first()
        if sub_membership and sub_membership.leave_date:
            sub_membership.leave_date = None
            sub_membership.save()
        else:
            join_date = None if subscription.waiting else datetime.date.today()
            SubscriptionMembership.objects.create(member=self, subscription=subscription, join_date=join_date)
        if primary:
            subscription.primary_member = self
            subscription.save()

    def leave_subscription(self, subscription=None, changedate=None):
        subscription = subscription or self.subscription_current
        sub_membership = self.subscriptionmembership_set.filter(subscription=subscription).first()
        membership_present = sub_membership and sub_membership.leave_date is None
        if membership_present and sub_membership.join_date is not None:
            changedate = changedate or datetime.date.today()
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
        if self.mobile_phone and self.mobile_phone.strip('0- '):
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
    member = models.ForeignKey('Member', on_delete=models.CASCADE, verbose_name=Config.vocabulary('member'))
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE, verbose_name=Config.vocabulary('subscription'))
    join_date = models.DateField(_('Beitrittsdatum'), null=True, blank=True, help_text=_('Erster Tag an dem {0} bezogen wird').format(Config.vocabulary('subscription')))
    leave_date = models.DateField(_('Austrittsdatum'), null=True, blank=True, help_text=_('Letzter Tag an dem {0} bezogen wird').format(Config.vocabulary('subscription')))

    def __str__(self):
        if not self.join_date:
            extra = _('Beitritt ausstehend')
        else:
            extra = f"{self.join_date} - {self.leave_date or _('Heute')}"
        return f"{self.member} - {self.subscription}: " + extra

    def clean(self):
        return check_sub_membership_consistency(self)

    def can_leave(self):
        enough_shares_to_leave = self.subscription.share_overflow - self.member.share_set.usable().count() >= 0
        return self.leave_date is None and self.member.is_cooperation_member and enough_shares_to_leave

    def waiting(self, date=None):
        return self.join_date is None or self.join_date > (date or datetime.date.today())

    def active(self, date=None):
        return not self.waiting(date) and not self.left(date)

    def leaves_before_end(self):
        """ true, if member left or will leave subscription before the subscription ends or ended
        """
        return self.leave_date is not None and (self.subscription.deactivation_date is None
                                                or self.leave_date < self.subscription.deactivation_date)

    def left(self, date=None):
        return self.leave_date is not None and self.leave_date <= (date or datetime.date.today())

    def co_members(self):
        return self.subscription.co_members(self.member)

    class Meta:
        unique_together = ('member', 'subscription')
        verbose_name = _('{}-Mitgliedschaft').format(Config.vocabulary('subscription'))
        verbose_name_plural = _('{}-Mitgliedschaften').format(Config.vocabulary('subscription'))
