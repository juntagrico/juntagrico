from django.contrib import admin
from django.contrib.auth.models import User

from juntagrico.admins import BaseAdmin
from juntagrico.admins.area_admin import AreaAdmin
from juntagrico.admins.assignment_admin import AssignmentAdmin
from juntagrico.admins.auth_admin import UserAdmin
from juntagrico.admins.billing_period_admin import BillingPeriodAdmin
from juntagrico.admins.delivery_admin import DeliveryAdmin
from juntagrico.admins.depot_admin import DepotAdmin
from juntagrico.admins.job_admin import JobAdmin
from juntagrico.admins.job_type_admin import JobTypeAdmin
from juntagrico.admins.list_message_admin import ListMessageAdmin
from juntagrico.admins.location_admin import LocationAdmin
from juntagrico.admins.member_admin import MemberAdmin, MemberAdminWithShares
from juntagrico.admins.one_time_job_admin import OneTimeJobAdmin
from juntagrico.admins.share_admin import ShareAdmin
from juntagrico.admins.subscription_admin import SubscriptionAdmin
from juntagrico.admins.subscription_product_admin import SubscriptionProductAdmin
from juntagrico.admins.subscription_type_admin import SubscriptionTypeAdmin, SubscriptionCategoryAdmin, \
    SubscriptionBundleAdmin
from juntagrico.admins.tour_admin import TourAdmin
from juntagrico.config import Config
from juntagrico.entity.billing import BillingPeriod
from juntagrico.entity.delivery import Delivery
from juntagrico.entity.location import Location
from juntagrico.entity.depot import Depot, Tour
from juntagrico.entity.jobs import Assignment, ActivityArea, JobExtra, JobExtraType, JobType, RecuringJob, OneTimeJob
from juntagrico.entity.listmessage import ListMessage
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member, SubscriptionMembership
from juntagrico.entity.share import Share
from juntagrico.entity.subs import Subscription
from juntagrico.entity.subtypes import SubscriptionBundle, SubscriptionType, SubscriptionProduct, SubscriptionCategory
from juntagrico.util import addons

# loading addons here so that we have the information about admin extensions stuff like inlines etc
addons.load_addons()

admin.site.register(Location, LocationAdmin)
admin.site.register(Depot, DepotAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(SubscriptionCategory, SubscriptionCategoryAdmin)
admin.site.register(SubscriptionBundle, SubscriptionBundleAdmin)
admin.site.register(SubscriptionType, SubscriptionTypeAdmin)
admin.site.register(SubscriptionProduct, SubscriptionProductAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Member, MemberAdminWithShares if Config.enable_shares() else MemberAdmin)
admin.site.register(SubscriptionMembership, BaseAdmin)
admin.site.register(ActivityArea, AreaAdmin)
admin.site.register(MailTemplate)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(JobExtra, BaseAdmin)
admin.site.register(JobExtraType, BaseAdmin)
admin.site.register(JobType, JobTypeAdmin)
admin.site.register(RecuringJob, JobAdmin)
admin.site.register(OneTimeJob, OneTimeJobAdmin)
admin.site.register(ListMessage, ListMessageAdmin)
admin.site.register(BillingPeriod, BillingPeriodAdmin)
if Config.enable_shares():
    admin.site.register(Share, ShareAdmin)

# override auth user admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
