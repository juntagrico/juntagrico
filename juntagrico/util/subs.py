from juntagrico.dao.memberdao import MemberDao


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
