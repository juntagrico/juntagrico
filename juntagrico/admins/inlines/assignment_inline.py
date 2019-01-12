from django.contrib import admin

from juntagrico.entity.jobs import Assignment


class AssignmentInline(admin.TabularInline):
    model = Assignment
    raw_id_fields = ['member']

    # can_delete = False

    # TODO: added these temporarily, need to be removed
    extra = 0
    max_num = 0

    def get_extra(self, request, obj=None, **kwargs):
        # TODO is this needed?
        # if 'copy_job' in request.path:
        #    return 0
        if obj is None:
            return 0
        return obj.free_slots()

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None:
            return 0
        return obj.slots
