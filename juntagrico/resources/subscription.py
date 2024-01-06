from import_export.fields import Field
from import_export.widgets import DecimalWidget

from ..entity.subs import Subscription, SubscriptionPart
from ..config import Config
from . import ModQuerysetModelResource, DateRangeResourceMixin


class SubscriptionResource(DateRangeResourceMixin, ModQuerysetModelResource):
    content = Field('size')

    status = Field('state_text')
    primary_member_name = Field('primary_member__get_name')
    primary_member_email = Field('primary_member__email')
    primary_member_phone = Field('primary_member__phone')
    primary_member_mobile = Field('primary_member__mobile')
    other_recipients_names = Field('other_recipients_names')
    depot = Field('depot__name')

    assignment_count = Field('assignment_count', widget=DecimalWidget())
    required_assignments = Field('required_assignments', widget=DecimalWidget())
    assignments_progress = Field('assignments_progress', widget=DecimalWidget())
    core_assignment_count = Field('core_assignment_count', widget=DecimalWidget())
    required_core_assignments = Field('required_core_assignments', widget=DecimalWidget())
    core_assignments_progress = Field('core_assignments_progress', widget=DecimalWidget())
    price = Field('price', widget=DecimalWidget())

    def update_queryset(self, queryset):
        return Subscription.objects.annotate_assignments_progress(self.start_date, self.end_date)

    class Meta:
        model = Subscription
        exclude = ('billable_ptr', 'polymorphic_ctype', 'future_depot', 'primary_member')
        export_order = ('id', 'content', 'status', 'nickname')
        name = Config.vocabulary('subscription_pl')


class SubscriptionPartResource(ModQuerysetModelResource):
    type_name = Field('type__name')
    subscription_id = Field('subscription__pk')
    is_extra = Field('type__size__product__is_extra')

    def update_queryset(self, queryset):
        return SubscriptionPart.objects.filter(subscription__in=queryset)

    class Meta:
        model = Subscription
        fields = ('id', 'subscription_id', 'type_name', 'creation_date', 'activation_date', 'cancellation_date', 'deactivation_date', 'is_extra')
        export_order = ('id', 'subscription_id')
        name = Config.vocabulary('subscription') + '-Bestandteile'
