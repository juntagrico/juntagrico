from django.contrib import admin

from juntagrico.admins.area_admin import AreaAdmin
from juntagrico.admins.assignment_admin import AssignmentAdmin
from juntagrico.admins.delivery_admin import DeliveryAdmin
from juntagrico.admins.depot_admin import DepotAdmin
from juntagrico.admins.extra_subscription_admin import ExtraSubscriptionAdmin
from juntagrico.admins.extra_subscription_category_admin import ExtraSubscriptionCategoryAdmin
from juntagrico.admins.extra_subscription_type_admin import ExtraSubscriptionTypeAdmin
from juntagrico.admins.job_admin import JobAdmin
from juntagrico.admins.job_extra_admin import JobExtraAdmin
from juntagrico.admins.job_extra_type_admin import JobExtraTypeAdmin
from juntagrico.admins.job_type_admin import JobTypeAdmin
from juntagrico.admins.list_message_admin import ListMessageAdmin
from juntagrico.admins.member_admin import MemberAdmin
from juntagrico.admins.one_time_job_admin import OneTimeJobAdmin
from juntagrico.admins.share_admin import ShareAdmin
from juntagrico.admins.subscription_admin import SubscriptionAdmin
from juntagrico.admins.subscription_size_admin import SubscriptionSizeAdmin
from juntagrico.admins.subscription_type_admin import SubscriptionTypeAdmin
from juntagrico.config import Config
from juntagrico.entity.billing import Bill, Payment
from juntagrico.entity.delivery import Delivery
from juntagrico.entity.depot import Depot
from juntagrico.entity.extrasubs import ExtraSubscription, ExtraSubscriptionType, ExtraSubscriptionCategory
from juntagrico.entity.jobs import Assignment, ActivityArea, JobExtra, JobExtraType, JobType, RecuringJob, OneTimeJob
from juntagrico.entity.listmessage import ListMessage
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription, ExtraSubBillingPeriod
from juntagrico.entity.subtypes import SubscriptionSize, SubscriptionType

admin.site.register(Depot, DepotAdmin)
admin.site.register(ExtraSubscription, ExtraSubscriptionAdmin)
admin.site.register(ExtraSubscriptionType, ExtraSubscriptionTypeAdmin)
admin.site.register(ExtraSubscriptionCategory, ExtraSubscriptionCategoryAdmin)
admin.site.register(SubscriptionSize, SubscriptionSizeAdmin)
admin.site.register(SubscriptionType, SubscriptionTypeAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(ActivityArea, AreaAdmin)
admin.site.register(MailTemplate)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(JobExtra, JobExtraAdmin)
admin.site.register(JobExtraType, JobExtraTypeAdmin)
admin.site.register(JobType, JobTypeAdmin)
admin.site.register(RecuringJob, JobAdmin)
admin.site.register(OneTimeJob, OneTimeJobAdmin)
admin.site.register(ListMessage, ListMessageAdmin)
admin.site.register(ExtraSubBillingPeriod)
if Config.enable_shares():
    admin.site.register(Share, ShareAdmin)
if Config.billing():
    admin.site.register(Bill)
    admin.site.register(Payment)
