# encoding: utf-8
from django.db import models
from django.db.models import signals

from juntagrico.entity.billing import *
from juntagrico.entity.extrasubs import *
from juntagrico.entity.subs import *
from juntagrico.entity.depot import *
from juntagrico.entity.member import *
from juntagrico.entity.share import *
from juntagrico.entity.jobs import *
from juntagrico.entity.mailing import *
from juntagrico.entity.delivery import *
from juntagrico.entity.listmessage import *


class SpecialRoles(models.Model):
    '''
    No instances should be created of this class it i just the place to create permissions
    like bookkeeper or operation group
    '''

    class Meta:
        permissions = (('is_operations_group', 'Benutzer ist in der BG'),
                       ('is_book_keeper', 'Benutzer ist Buchhalter'),
                       ('new_subscription', 'Benutzer über Abobestellungen informieren'),
                       ('can_send_mails', 'Benutzer kann im System Emails versenden'),
                       ('can_use_general_email', 'Benutzer kann General Email Adresse verwenden'),)


signals.post_save.connect(Member.create, sender=Member)
signals.post_delete.connect(Member.post_delete, sender=Member)
signals.pre_save.connect(Member.pre_save, sender=Member)
signals.pre_save.connect(Job.pre_save, sender=Job)
signals.post_init.connect(Job.post_init, sender=Job)
signals.pre_save.connect(RecuringJob.pre_save, sender=RecuringJob)
signals.post_init.connect(RecuringJob.post_init, sender=RecuringJob)
signals.pre_save.connect(OneTimeJob.pre_save, sender=OneTimeJob)
signals.post_init.connect(OneTimeJob.post_init, sender=OneTimeJob)
signals.pre_save.connect(Subscription.pre_save, sender=Subscription)
signals.post_init.connect(Subscription.post_init, sender=Subscription)
signals.post_init.connect(ExtraSubscription.post_init,
                          sender=ExtraSubscription)
signals.pre_save.connect(ExtraSubscription.pre_save, sender=ExtraSubscription)
signals.pre_save.connect(Assignment.pre_save, sender=Assignment)
signals.post_save.connect(Share.create, sender=Share)
