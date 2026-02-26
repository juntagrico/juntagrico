from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.translation import gettext as _
from polymorphic.admin import GenericStackedPolymorphicInline
from polymorphic.formsets import BaseGenericPolymorphicInlineFormSet

from juntagrico.admins import AreaCoordinatorInlineMixin
from juntagrico.entity.contact import Contact, MemberContact, EmailContact, PhoneContact, TextContact
from juntagrico.entity.member import Member


class ContactInlineFormSet(BaseGenericPolymorphicInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        # If user can't view all members, limit options to specific members
        obj = self.instance
        member_field = form.fields.get('member')
        if obj and member_field and not isinstance(member_field.widget, ForeignKeyRawIdWidget):
            options = obj.get_contact_options() or Member.objects.none()
            member_field.queryset = (
                options | Member.objects.filter(membercontact__in=obj.contact_set.all())
            ).distinct()


class ContactInline(GenericStackedPolymorphicInline):
    class MemberContactInline(GenericStackedPolymorphicInline.Child):
        model = MemberContact
        fields = ('member', 'display', 'sort_order')

        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            # make member raw_id field, if user can see members
            if request.user.has_perm('juntagrico.view_member'):
                self.raw_id_fields = ('member',)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
    formset = ContactInlineFormSet
    child_inlines = (
        MemberContactInline,
        EmailContactInline,
        PhoneContactInline,
        TextContactInline,
    )


class ContactInlineForJob(AreaCoordinatorInlineMixin, ContactInline):
    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None and not request.user.has_perm('juntagrico.view_member'):
            # area admins must safe job(types) first, because contact selection depends on area of job
            self.verbose_name_plural += _(' (Kann erst nach dem Speichern eingestellt werden)')
            return 0
        return super().get_max_num(request, obj, **kwargs)


class ContactInlineForArea(ContactInlineForJob):
    coordinator_access = 'can_modify_area'
