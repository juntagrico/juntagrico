from django.db.models import Q
from django.utils.translation import gettext as _

from import_export import resources
from import_export.fields import Field
from import_export.widgets import ManyToManyWidget, DecimalWidget

from ..entity.jobs import ActivityArea, Job
from ..entity.member import Member
from ..config import Config
from . import ModQuerysetModelResource, DateRangeResourceMixin


class MemberResource(resources.ModelResource):
    class Meta:
        model = Member
        exclude = ('user',)
        widgets = {
            'id': {'coerce_to_string': False},
            'birthday': {'coerce_to_string': False},
            'confirmed': {'coerce_to_string': False},
            'reachable_by_email': {'coerce_to_string': False},
            'cancellation_date': {'coerce_to_string': False},
            'deactivation_date': {'coerce_to_string': False},
            'end_date': {'coerce_to_string': False},
            'number': {'coerce_to_string': False},
        }
        name = Config.vocabulary('member_pl')


class MemberWithAssignmentsAndAreaResource(DateRangeResourceMixin, ModQuerysetModelResource):
    depot = Field('subscription_current__depot__name', 'depot', readonly=True)
    areas = Field('areas', widget=ManyToManyWidget(ActivityArea, field='name'), readonly=True)
    assignment_count = Field('assignment_count', widget=DecimalWidget(), readonly=True)
    core_assignment_count = Field('core_assignment_count', widget=DecimalWidget(), readonly=True)

    def update_queryset(self, queryset):
        return queryset.annotate_all_assignment_count(self.start_date, self.end_date)

    class Meta:
        model = Member
        exclude = ('user',)
        export_order = ('id', 'first_name', 'last_name')
        name = _("{0} mit {1}, Tätigkeitsbereich und {2}").format(Config.vocabulary('member_pl'),
                                                                  Config.vocabulary('depot'),
                                                                  Config.vocabulary('assignment_pl'))


class MemberAssignmentsPerArea(DateRangeResourceMixin, ModQuerysetModelResource):
    name = Field('get_name', 'name')

    def get_fields(self):
        # create a field for each area dynamically
        self.fields.update({
            area.name: Field(f'{area.id}assignment_count', area.name)
            for area in ActivityArea.objects.all()
        })
        return super().get_fields()

    def update_queryset(self, queryset):
        for area in ActivityArea.objects.all():
            queryset = queryset.annotate_assignment_count(
                self.start_date, self.end_date,
                prefix=str(area.id),
                assignment__job__in=Job.objects.filter(
                    Q(RecuringJob___type__activityarea=area.pk) |
                    Q(OneTimeJob___activityarea=area.pk)
                )
            )
        return queryset

    class Meta:
        model = Member
        fields = ('id', 'name')
        export_order = fields
        name = _("{0}: {1} nach Tätigkeitsbereich").format(Config.vocabulary('member_pl'),
                                                           Config.vocabulary('assignment_pl'))
