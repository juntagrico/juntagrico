from django.contrib import admin
from django.contrib.auth.models import User

from juntagrico import admins
from juntagrico.admins.member_admin import MemberAdmin, JuntagricoUserAdmin, MemberAdminWithShares
from juntagrico.admins.share_admin import ShareAdmin
from juntagrico.entity.mailing import MailTemplate
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.util import addons
from juntagrico.config import Config

# loading addons here so that we have the information about admin extensions stuff like inlines etc
addons.load_addons()

admin.site.register(Member, MemberAdminWithShares if Config.enable_shares() else MemberAdmin)
if Config.enable_shares():
    admin.site.register(Share, ShareAdmin)

admin.site.register(MailTemplate)

admin.site.unregister(User)
admin.site.register(User, JuntagricoUserAdmin)
