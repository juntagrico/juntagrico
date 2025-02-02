from django.dispatch import Signal

from juntagrico.mailer import adminnotification, membernotification

subscribed = Signal()
canceled = Signal()

''' job related signals'''
job_canceled = Signal()
job_time_changed = Signal()

''' area signals '''
area_joined = Signal()
area_left = Signal()

'''subscription related signals'''
sub_created = Signal()
sub_activated = Signal()
sub_deactivated = Signal()
sub_canceled = Signal()
depot_changed = Signal()
depot_change_confirmed = Signal()

''' extra subscription signals '''
extra_sub_activated = Signal()
extra_sub_deactivated = Signal()

''' subscription part signals '''
sub_part_activated = Signal()
sub_part_deactivated = Signal()

''' share signals '''
share_created = Signal()
share_canceled = Signal()

''' member signals '''
member_created = Signal()
member_canceled = Signal()  # DEPRECATED
member_deactivated = Signal()
assignment_changed = Signal()


''' Signal Receivers '''


def on_depot_changed(sender, **kwargs):
    adminnotification.member_changed_depot(**kwargs)


def on_share_canceled(sender, instance, **kwargs):
    adminnotification.share_canceled(instance, **kwargs)


def on_depot_change_confirmed(sender, instance, **kwargs):
    membernotification.depot_changed(instance, **kwargs)


def on_member_canceled(sender, instance, **kwargs):
    adminnotification.member_canceled(instance, **kwargs)


def on_job_subscribed(sender, **kwargs):
    job = kwargs.get('instance')
    member = kwargs.get('member')
    initial_count = kwargs.get('initial_count')
    count = kwargs.get('count')
    if initial_count == 0 and count > 0:
        membernotification.job_signup(member.email, job, count)
        adminnotification.member_subscribed_to_job(job, **kwargs)
    elif count == 0:
        membernotification.job_unsubscribed(member.email, job, initial_count)
        adminnotification.member_unsubscribed_from_job(job, **kwargs)
    else:
        membernotification.job_subscription_changed(member.email, job, count)
        adminnotification.member_changed_job_subscription(job, **kwargs)


def on_assignment_changed(sender, **kwargs):
    member = kwargs.get('instance')
    editor = kwargs.get('editor')
    count = kwargs.get('count')
    if member != editor:  # don't send this notification if editor changed their own assignment
        if count == 0:
            membernotification.assignment_removed(member.email, **kwargs)
        else:
            membernotification.assignment_changed(member.email, **kwargs)
    if count == 0:
        adminnotification.assignment_removed(**kwargs)
    else:
        adminnotification.assignment_changed(**kwargs)
