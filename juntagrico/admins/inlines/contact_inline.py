from polymorphic.admin import GenericStackedPolymorphicInline

from juntagrico.entity.contact import Contact, MemberContact, EmailContact, PhoneContact, TextContact


class ContactInline(GenericStackedPolymorphicInline):
    class MemberContactInline(GenericStackedPolymorphicInline.Child):
        model = MemberContact
        fields = ('member', 'display', 'sort_order')
        raw_id_fields = ('member',)

    class EmailContactInline(GenericStackedPolymorphicInline.Child):
        model = EmailContact
        fields = ('email', 'sort_order')

    class PhoneContactInline(GenericStackedPolymorphicInline.Child):
        model = PhoneContact
        fields = ('phone', 'sort_order')

    class TextContactInline(GenericStackedPolymorphicInline.Child):
        model = TextContact
        fields = ('text', 'sort_order')

    model = Contact
    child_inlines = (
        MemberContactInline,
        EmailContactInline,
        PhoneContactInline,
        TextContactInline,
    )
