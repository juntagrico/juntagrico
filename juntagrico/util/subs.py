from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.mailer import membernotification


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
        ap = (assignments / subscription.required_assignments * 100) if subscription.required_assignments != 0 else 100
        cap = (core_assignments / subscription.required_core_assignments * 100) if subscription.required_core_assignments != 0 else 100
        subscriptions_list.append({
            'subscription': subscription,
            'assignments': assignments,
            'assignments_progress': ap,
            'core_assignments': core_assignments,
            'core_assignments_progress': cap,
        })
    return subscriptions_list


def activate_future_depots():
    for subscription in SubscriptionDao.subscritions_with_future_depots():
        subscription.depot = subscription.future_depot
        subscription.future_depot = None
        subscription.save()
        emails = []
        for member in subscription.recipients:
            emails.append(member.email)
        membernotification.depot_changed(emails, subscription.depot)
