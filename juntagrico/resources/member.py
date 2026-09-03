from django.utils.translation import gettext as _
from import_export import resources

from import_export.fields import Field
from import_export.widgets import ManyToManyWidget, DecimalWidget

from ..entity.jobs import ActivityArea, Job
from ..entity.member import Member
from ..config import Config
from . import DateRangeResourceMixin, TranslatedModelResource


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


class TranslatedMemberResource(TranslatedModelResource, MemberResource):
    class Meta:
        verbose_names = {
            'subscriptions': Config.vocabulary('subscription_pl'),
        }


class MemberWithAssignmentsAndAreaResource(DateRangeResourceMixin, resources.ModelResource):
    depot = Field('subscription_current__depot__name', 'depot', readonly=True)
    areas = Field('areas', widget=ManyToManyWidget(ActivityArea, field='name'), readonly=True)
    assignment_count = Field('assignment_count', widget=DecimalWidget(), readonly=True)
    core_assignment_count = Field('core_assignment_count', widget=DecimalWidget(), readonly=True)

    def filter_export(self, queryset, **kwargs):
        return queryset.annotate_all_assignment_count(self.start_date, self.end_date)

    class Meta:
        model = Member
        exclude = ('user',)
        export_order = ('id', 'first_name', 'last_name')
        name = _("{0} mit {1}, Tätigkeitsbereich und {2}").format(Config.vocabulary('member_pl'),
                                                                  Config.vocabulary('depot'),
                                                                  Config.vocabulary('assignment_pl'))


class TranslatedMemberWithAssignmentsAndAreaResource(MemberWithAssignmentsAndAreaResource, TranslatedModelResource):
    class Meta:
        verbose_names = {
            'subscriptions': Config.vocabulary('subscription_pl'),
            'depot': Config.vocabulary('depot'),
            'areas': _('Tätigkeitsbereiche'),
            'assignment_count': _('Arbeitseinsätze'),
            'core_assignment_count': _('Kern Arbeitseinsätze'),
        }


class MemberAssignmentsPerArea(DateRangeResourceMixin, resources.ModelResource):
    name = Field('get_name', 'name')

    def before_export(self, queryset, **kwargs):
        # create a field for each area dynamically
        self.fields.update(
            {
                area.name: Field(f'{area.id}assignment_count', area.name)
                for area in ActivityArea.objects.all()
            }
        )
        kwargs['export_fields'] += [area.name for area in ActivityArea.objects.all()]

    def filter_export(self, queryset, **kwargs):
        for area in ActivityArea.objects.all():
            queryset = queryset.annotate_assignment_count(
                self.start_date,
                self.end_date,
                prefix=str(area.id),
                assignment__job__in=Job.objects.in_area(area),
            )
        return queryset

    class Meta:
        model = Member
        fields = ('id', 'name')
        export_order = fields
        name = _("{0}: {1} nach Tätigkeitsbereich").format(Config.vocabulary('member_pl'),
                                                           Config.vocabulary('assignment_pl'))
