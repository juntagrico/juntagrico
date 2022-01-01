from polymorphic.admin import StackedPolymorphicInline
from juntagrico.entity.jobs import Contact, MemberContact, EmailContact, PhoneContact, TextContact


class ContactInline(StackedPolymorphicInline):
    class MemberContactInline(StackedPolymorphicInline.Child):
        model = MemberContact
        fields = ('member', 'display', 'sort_order')
        raw_id_fields = ('member',)

    class EmailContactInline(StackedPolymorphicInline.Child):
        model = EmailContact
        fields = ('email', 'sort_order')

    class PhoneContactInline(StackedPolymorphicInline.Child):
        model = PhoneContact
        fields = ('phone', 'sort_order')

    class TextContactInline(StackedPolymorphicInline.Child):
        model = TextContact
        fields = ('text', 'sort_order')

    model = Contact
    child_inlines = (
        MemberContactInline,
        EmailContactInline,
        PhoneContactInline,
        TextContactInline,
    )
