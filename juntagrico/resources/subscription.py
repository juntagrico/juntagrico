from django.utils.translation import gettext as _
from import_export import resources
from import_export.fields import Field
from import_export.widgets import DecimalWidget, IntegerWidget

from . import DateRangeResourceMixin, TranslatedModelResource
from ..config import Config
from ..entity.subs import Subscription, SubscriptionPart


class SubscriptionResource(DateRangeResourceMixin, resources.ModelResource):
    content = Field('size')

    status = Field('state_text')
    primary_member_name = Field('primary_member__get_name')
    primary_member_email = Field('primary_member__email')
    primary_member_phone = Field('primary_member__phone')
    primary_member_mobile = Field('primary_member__mobile')
    primary_member_street = Field('primary_member__addr_street')
    primary_member_zipcode = Field('primary_member__addr_zipcode')
    primary_member_location = Field('primary_member__addr_location')
    co_members = Field('co_members')
    depot = Field('depot__name')

    assignment_count = Field('assignment_count', widget=DecimalWidget(coerce_to_string=False))
    required_assignments = Field('required_assignments', widget=DecimalWidget(coerce_to_string=False))
    assignments_progress = Field('assignments_progress', widget=DecimalWidget(coerce_to_string=False))
    core_assignment_count = Field('core_assignment_count', widget=DecimalWidget(coerce_to_string=False))
    required_core_assignments = Field('required_core_assignments', widget=DecimalWidget(coerce_to_string=False))
    core_assignments_progress = Field('core_assignments_progress', widget=DecimalWidget(coerce_to_string=False))
    price = Field('price', widget=DecimalWidget())

    def filter_export(self, queryset, **kwargs):
        return queryset.annotate_assignments_progress(self.start_date, self.end_date)

    def dehydrate_co_members(self, subscription):
        return ', '.join(str(m) for m in subscription.co_members())

    class Meta:
        model = Subscription
        exclude = ('billable_ptr', 'polymorphic_ctype', 'future_depot', 'primary_member')
        widgets = {
            'id': {'coerce_to_string': False},
            'creation_date': {'coerce_to_string': False},
            'activation_date': {'coerce_to_string': False},
            'cancellation_date': {'coerce_to_string': False},
            'deactivation_date': {'coerce_to_string': False},
        }
        export_order = ('id', 'identifier', 'content', 'status', 'nickname')
        name = Config.vocabulary('subscription_pl')


class TranslatedSubscriptionResource(SubscriptionResource, TranslatedModelResource):
    class Meta:
        verbose_names = {
            'content': _('Inhalt'),
            'status': _('Status'),
            'types': _('Typen'),
            'depot': Config.vocabulary('depot'),
            'primary_member_name': _('Name HauptbezieherIn'),
            'primary_member_email': _('E-Mail HauptbezieherIn'),
            'primary_member_phone': _('Telefon HauptbezieherIn'),
            'primary_member_mobile': _('Mobil HauptbezieherIn'),
            'primary_member_street': _('Strasse HauptbezieherIn'),
            'primary_member_zipcode': _('PLZ HauptbezieherIn'),
            'primary_member_location': _('Ort HauptbezieherIn'),
            'co_members': Config.vocabulary('co_member_pl'),
            'assignment_count': _('Arbeitseinsätze'),
            'required_assignments': _('benötigte Arbeitseinsätze'),
            'assignments_progress': _('Arbeitseinsätze Status'),
            'core_assignment_count': _('Kern-Arbeitseinsätze'),
            'required_core_assignments': _('Benötigte Kern-Arbeitseinsätze'),
            'core_assignments_progress': _('Kern-Arbeitseinsätze Status'),
            'price': _('Preis'),
        }


class SubscriptionPartResource(resources.ModelResource):
    type_name = Field('type__name')
    subscription_id = Field('subscription__pk', widget=IntegerWidget(coerce_to_string=False))
    is_extra = Field('type__is_extra')

    def filter_export(self, queryset, **kwargs):
        return SubscriptionPart.objects.filter(subscription__in=queryset)

    class Meta:
        model = Subscription
        fields = ('id', 'subscription_id', 'type_name', 'creation_date', 'activation_date', 'cancellation_date', 'deactivation_date', 'is_extra')
        widgets = {
            'id': {'coerce_to_string': False},
            'creation_date': {'coerce_to_string': False},
            'activation_date': {'coerce_to_string': False},
            'cancellation_date': {'coerce_to_string': False},
            'deactivation_date': {'coerce_to_string': False},
        }
        export_order = ('id', 'subscription_id')
        name = Config.vocabulary('subscription') + '-Bestandteile'


class TranslatedSubscriptionPartResource(SubscriptionPartResource, TranslatedModelResource):
    class Meta:
        verbose_names = {
            'subscription_id': Config.vocabulary('subscription') + ' ID',
            'type_name': _('Typ-Name'),
            'is_extra': _('Ist Zusatzabo'),
        }
