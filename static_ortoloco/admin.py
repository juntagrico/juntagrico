from django.contrib import admin
from static_ortoloco.models import *

class PolitolocoAdmin(admin.ModelAdmin):
    search_fields = ('email',)

admin.site.register(StaticContent)
admin.site.register(Media)
admin.site.register(Download)
admin.site.register(Link)
admin.site.register(Document)
admin.site.register(Politoloco, PolitolocoAdmin)
