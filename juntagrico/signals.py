from django.dispatch import Signal

from juntagrico.mailer import adminnotification

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

''' extra subscription signals '''
extra_sub_activated = Signal()
extra_sub_deactivated = Signal()

''' subscription part signals '''
sub_part_activated = Signal()
sub_part_deactivated = Signal()

''' depot signals '''
depot_changed = Signal()

''' share signals '''
share_created = Signal()
share_canceled = Signal()

''' member signals '''
member_created = Signal()
member_canceled = Signal()
member_deactivated = Signal()


''' Signal Receivers '''


def on_depot_changed(sender, **kwargs):
    adminnotification.member_changed_depot(**kwargs)
