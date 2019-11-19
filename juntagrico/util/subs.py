from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.mailer import send_depot_changed


def subscriptions_with_assignments(subscriptions):
    subscriptions_list = []
    for subscription in subscriptions:
        assignments = 0
        core_assignments = 0
        members = MemberDao.members_with_assignments_count_in_subscription(
            subscription)
        for member in members:
            assignments += member.assignment_count \
                if member.assignment_count is not None else 0
            core_assignments += member.core_assignment_count \
                if member.core_assignment_count is not None else 0
        subscriptions_list.append({
            'subscription': subscription,
            'assignments': assignments,
            'core_assignments': core_assignments
        })
    return subscriptions_list


def process_future_depots():
    for subscription in SubscriptionDao.subscritions_with_future_depots():
        subscription.depot = subscription.future_depot
        subscription.future_depot = None
        subscription.save()
        emails = []
        for member in subscription.recipients:
            emails.append(member.email)
        send_depot_changed(emails, subscription.depot)


def process_trial_subs():
    trial_types = SubscriptionTypeDao.get_trial()
    for ttype in trial_types.all():
        for sub in ttype.subscription_set.filter(active=True):
            if sub.remaining_trial_days < 1:
                sub.active = False
                sub.save()
                # TODO notify all who need notification
