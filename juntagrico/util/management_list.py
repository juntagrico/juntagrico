from django.db.models import Prefetch, F

from juntagrico.dao.subscriptionmembershipdao import SubscriptionMembershipDao


def get_changedate(request):
    change_date = request.session.get('changedate', None)
    can_change_date = change_date is None
    return {'change_date': change_date,
            'can_change_date': can_change_date}


def prefetch_for_list(members):
    members = members.defer('notes').prefetch_related('areas').annotate(userid=F('user__id'))
    return members.prefetch_related(
        Prefetch('subscriptionmembership_set',
                 queryset=SubscriptionMembershipDao.current_of_members(members),
                 to_attr='current_subscriptionmembership'),
        'current_subscriptionmembership__subscription'
    )
