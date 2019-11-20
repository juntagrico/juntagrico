from juntagrico.dao.memberdao import MemberDao
from juntagrico.mailer import send_subscription_canceled


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


def cancel_sub(subscription, end_date, message):
    if subscription.active is True and subscription.canceled is False:
        subscription.canceled = True
        subscription.end_date = end_date
        subscription.save()

        send_subscription_canceled(subscription, message)
    elif subscription.active is False and subscription.deactivation_date is None:
        subscription.delete()


def cancel_extra_sub(extra):
    if extra.active is True:
        extra.canceled = True
        extra.save()
    elif extra.active is False and extra.deactivation_date is None:
        extra.delete()
