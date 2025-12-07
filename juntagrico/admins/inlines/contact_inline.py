from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.forms import ModelForm
from django.utils.translation import gettext as _
from polymorphic.admin import GenericStackedPolymorphicInline

from juntagrico.admins import AreaCoordinatorInlineMixin
from juntagrico.entity.contact import Contact, MemberContact, EmailContact, PhoneContact, TextContact
from juntagrico.entity.member import Member


class ContactInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # handle extra kwarg
        self.members = kwargs.pop('members')
        super().__init__(*args, **kwargs)


class MemberContactInlineForm(ContactInlineForm):
    def __init__(self, *args, **kwargs):
        # If user can't view all members, limit options to specific members
        super().__init__(*args, **kwargs)
        if not isinstance(self.fields["member"].widget, ForeignKeyRawIdWidget):
            qs = self.members or Member.objects.none()
            if self.instance.id:
                qs = (qs | Member.objects.filter(pk=self.instance.member.pk)).distinct()
            self.fields["member"].queryset = qs


class ContactInline(GenericStackedPolymorphicInline):
    class MemberContactInline(GenericStackedPolymorphicInline.Child):
        model = MemberContact
        fields = ('member', 'display', 'sort_order')
        form = MemberContactInlineForm

        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            # make member raw_id field, if user can see members
            if request.user.has_perm('juntagrico.view_member'):
                self.raw_id_fields = ('member',)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class EmailContactInline(GenericStackedPolymorphicInline.Child):
        model = EmailContact
        fields = ('email', 'sort_order')
        form = ContactInlineForm

    class PhoneContactInline(GenericStackedPolymorphicInline.Child):
        model = PhoneContact
        fields = ('phone', 'sort_order')
        form = ContactInlineForm

    class TextContactInline(GenericStackedPolymorphicInline.Child):
        model = TextContact
        fields = ('text', 'sort_order')
        form = ContactInlineForm

    model = Contact
    child_inlines = (
        MemberContactInline,
        EmailContactInline,
        PhoneContactInline,
        TextContactInline,
    )


class ContactInlineForJob(AreaCoordinatorInlineMixin, ContactInline):
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # pass available members for form
        area = self.get_area(obj)
        formset.get_form_kwargs = lambda s, i: {'members': area.coordinators.all() if area else None}
        return formset

    def get_max_num(self, request, obj=None, **kwargs):
        if obj is None and not request.user.has_perm('juntagrico.view_member'):
            # area admins must safe job(types) first, because contact selection depends on area of job
            self.verbose_name_plural += _(' (Kann erst nach dem Speichern eingestellt werden)')
            return 0
        return super().get_max_num(request, obj, **kwargs)


class ContactInlineForArea(ContactInlineForJob):
    coordinator_access = 'can_modify_area'
