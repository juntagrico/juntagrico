from import_export.fields import Field

from . import ModQuerysetModelResource
from ..config import Config
from ..entity.share import Share


class ShareResource(ModQuerysetModelResource):
    member_first_name = Field('member__first_name')
    member_last_name = Field('member__last_name')
    member_email = Field('member__email')

    class Meta:
        model = Share
        exclude = ('billable_ptr', 'polymorphic_ctype', 'member')
        widgets = {
            'id': {'coerce_to_string': False},
            'number': {'coerce_to_string': False},
            'creation_date': {'coerce_to_string': False},
            'paid_date': {'coerce_to_string': False},
            'issue_date': {'coerce_to_string': False},
            'booking_date': {'coerce_to_string': False},
            'cancelled_date': {'coerce_to_string': False},
            'termination_date': {'coerce_to_string': False},
            'payback_date': {'coerce_to_string': False},
            'sent_back': {'coerce_to_string': False},
        }
        export_order = ('id', 'number')
        name = Config.vocabulary('share_pl')
