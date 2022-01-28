from django.dispatch import Signal

''' job related signals'''
job_canceled = Signal()
job_time_changed = Signal()

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

''' share signals '''
share_created = Signal()
share_canceled = Signal()

''' member signals '''
member_created = Signal()
member_canceled = Signal()
member_deactivated = Signal()
