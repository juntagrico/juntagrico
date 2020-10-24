from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.dao.subscriptionmembershipdao import SubscriptionMembershipDao


def sub_membership_pre_save(sender, instance, **kwargs):
    check_sub_membership_consistency(instance)


def check_sub_membership_consistency(instance):
    subscription = instance.subscription
    member = instance.member
    check_sub_membership_consistency_ms(member, subscription)


def check_sub_membership_consistency_ms(member, subscription):
    if subscription.state == 'waiting' and SubscriptionMembershipDao.get_other_waiting_for_member(member,
                                                                                                  subscription).count() > 0:
        raise ValidationError(
            _('Diese/r/s {} hat bereits ein/e/n zukünftige/n/s {}').format(Config.vocabulary('member'),
                                                                           Config.vocabulary('subscription')),
            code='invalid')
    if subscription.state == 'active' and SubscriptionMembershipDao.get_other_active_for_member(member,
                                                                                                subscription).count() > 0:
        raise ValidationError(
            _('Diese/r/s {} hat bereits ein/e/n {}').format(Config.vocabulary('member'),
                                                            Config.vocabulary('subscription')),
            code='invalid')
