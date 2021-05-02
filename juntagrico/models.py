from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.utils.translation import gettext as _

import juntagrico
from juntagrico.config import Config
from juntagrico.entity.jobs import Assignment, OneTimeJob, RecuringJob, Job
from juntagrico.entity.member import Member, SubscriptionMembership
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, SubscriptionPart
from juntagrico.lifecycle.job import job_pre_save, handle_job_canceled, handle_job_time_changed
from juntagrico.lifecycle.member import member_pre_save, member_post_save, handle_member_deactivated, \
    handle_member_created
from juntagrico.lifecycle.share import share_post_save, handle_share_created, share_pre_save
from juntagrico.lifecycle.simplestate import handle_simple_deactivated, handle_simple_activated
from juntagrico.lifecycle.sub import sub_pre_save, handle_sub_canceled, handle_sub_deactivated, handle_sub_activated, \
    sub_post_save, handle_sub_created
from juntagrico.lifecycle.submembership import sub_membership_pre_save
from juntagrico.lifecycle.subpart import sub_part_pre_save
from juntagrico.util.signals import register_entities_for_post_init_and_save


class SpecialRoles(models.Model):
    '''
    No instances should be created of this class it is just the place to create permissions
    like bookkeeper or operation group
    '''

    class Meta:
        permissions = (('is_operations_group', _('Benutzer ist in der BG')),
                       ('is_book_keeper', _('Benutzer ist Buchhalter')),
                       ('can_send_mails', _('Benutzer kann im System Emails versenden')),
                       ('can_use_general_email', _('Benutzer kann General Email Adresse verwenden')),
                       ('depot_list_notification',
                        _('Benutzer wird bei {0}-Listen-Erstellung informiert').format(Config.vocabulary('depot'))),
                       ('can_view_exports', _('Benutzer kann Exporte öffnen')),
                       ('can_view_lists', _('Benutzer kann Listen öffnen')),)


''' non lifecycle related signals '''
signals.pre_save.connect(Member.create, sender=Member)
signals.post_delete.connect(Member.post_delete, sender=Member)
signals.pre_save.connect(Assignment.pre_save, sender=Assignment)
''' lifecycle signal handling'''
''' job signal handling '''
signals.pre_save.connect(job_pre_save, sender=OneTimeJob)
signals.pre_save.connect(job_pre_save, sender=RecuringJob)
signals.pre_save.connect(job_pre_save, sender=Job)
juntagrico.signals.job_canceled.connect(handle_job_canceled, sender=OneTimeJob)
juntagrico.signals.job_canceled.connect(handle_job_canceled, sender=RecuringJob)
juntagrico.signals.job_time_changed.connect(handle_job_time_changed, sender=OneTimeJob)
juntagrico.signals.job_time_changed.connect(handle_job_time_changed, sender=RecuringJob)
''' subscription signal handling '''
signals.pre_save.connect(sub_pre_save, sender=Subscription)
signals.post_save.connect(sub_post_save, sender=Subscription)
juntagrico.signals.sub_created.connect(handle_sub_created, sender=Subscription)
juntagrico.signals.sub_activated.connect(handle_sub_activated, sender=Subscription)
juntagrico.signals.sub_deactivated.connect(handle_sub_deactivated, sender=Subscription)
juntagrico.signals.sub_canceled.connect(handle_sub_canceled, sender=Subscription)
''' subscription part handling'''
signals.pre_save.connect(sub_part_pre_save, sender=SubscriptionPart)
juntagrico.signals.extra_sub_activated.connect(handle_simple_activated, sender=SubscriptionPart)
juntagrico.signals.extra_sub_deactivated.connect(handle_simple_deactivated, sender=SubscriptionPart)
''' subscription membership handling '''
signals.pre_save.connect(sub_membership_pre_save, sender=SubscriptionMembership)
''' share handling '''
signals.pre_save.connect(share_pre_save, sender=Share)
signals.post_save.connect(share_post_save, sender=Share)
juntagrico.signals.share_created.connect(handle_share_created, sender=Share)
''' member handling '''
signals.pre_save.connect(member_pre_save, sender=Member)
signals.post_save.connect(member_post_save, sender=Member)
juntagrico.signals.member_created.connect(handle_member_created, sender=Member)
juntagrico.signals.member_deactivated.connect(handle_member_deactivated, sender=Member)
''' lifecycle all post init'''
register_entities_for_post_init_and_save()

'''monkey patch User email method'''


def member_email(self):
    return self.member.email


User.member__email = property(member_email)

User.EMAIL_FIELD = 'member__email'
