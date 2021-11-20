from polymorphic.admin import StackedPolymorphicInline
from juntagrico.entity.jobs import Contact, MemberContact, EmailContact, PhoneContact, TextContact


class ContactInline(StackedPolymorphicInline):
    class MemberContactInline(StackedPolymorphicInline.Child):
        model = MemberContact
        fields = ('member', 'display')
        raw_id_fields = ('member',)

    class EmailContactInline(StackedPolymorphicInline.Child):
        model = EmailContact
        fields = ('email',)

    class PhoneContactInline(StackedPolymorphicInline.Child):
        model = PhoneContact
        fields = ('phone',)

    class TextContactInline(StackedPolymorphicInline.Child):
        model = TextContact
        fields = ('text',)

    model = Contact
    child_inlines = (
        MemberContactInline,
        EmailContactInline,
        PhoneContactInline,
        TextContactInline,
    )
