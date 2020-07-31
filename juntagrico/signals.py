from django.dispatch import Signal

''' job related signals'''
job_canceled = Signal(providing_args=['instance'])
job_time_changed = Signal(providing_args=['instance'])

'''subscription related signals'''
sub_created = Signal(providing_args=['instance'])
sub_activated = Signal(providing_args=['instance'])
sub_deactivated = Signal(providing_args=['instance'])
sub_canceled = Signal(providing_args=['instance'])

''' extra subscription signals '''
extra_sub_activated = Signal(providing_args=['instance'])
extra_sub_deactivated = Signal(providing_args=['instance'])

''' subscription part signals '''
sub_part_activated = Signal(providing_args=['instance'])
sub_part_deactivated = Signal(providing_args=['instance'])

''' share signals '''
share_created = Signal(providing_args=['instance'])
share_canceled = Signal(providing_args=['instance'])

''' member signals '''
member_created = Signal(providing_args=['instance'])
member_canceled = Signal(providing_args=['instance'])
member_deactivated = Signal(providing_args=['instance'])
