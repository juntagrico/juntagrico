from django.contrib import admin

from juntagrico.entity.jobs import Assignment


class AssignmentInline(admin.TabularInline):
    model = Assignment
    raw_id_fields = ['member']

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        if not obj.infinite_slots:
            return obj.free_slots
        return super().get_extra(request, obj, **kwargs)

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        if not obj.infinite_slots:
            return obj.slots
        return super().get_max_num(request, obj, **kwargs)
