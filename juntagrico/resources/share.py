from import_export.fields import Field

from ..entity.share import Share
from ..config import Config
from . import ModQuerysetModelResource


class ShareResource(ModQuerysetModelResource):
    member_first_name = Field('member__first_name')
    member_last_name = Field('member__last_name')
    member_email = Field('member__email')

    class Meta:
        model = Share
        exclude = ('billable_ptr', 'polymorphic_ctype', 'member')
        export_order = ('id', 'number')
        name = Config.vocabulary('share_pl')
