from import_export import resources
from import_export.fields import Field

from ..config import Config
from ..entity.membership import Membership


class MembershipResource(resources.ModelResource):
    account_first_name = Field('account__first_name')
    account_last_name = Field('account__last_name')
    account_email = Field('account__email')

    class Meta:
        model = Membership
        exclude = ('account',)
        widgets = {
            'id': {'coerce_to_string': False},
            'number': {'coerce_to_string': False},
            'creation_date': {'coerce_to_string': False},
            'activation_date': {'coerce_to_string': False},
            'cancellation_date': {'coerce_to_string': False},
            'deactivation_date': {'coerce_to_string': False},
        }
        export_order = ('id', 'number')
        name = Config.vocabulary('membership_pl')
