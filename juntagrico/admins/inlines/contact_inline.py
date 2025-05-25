from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.forms import ModelForm
from polymorphic.admin import GenericStackedPolymorphicInline

from juntagrico.admins import AreaCoordinatorInlineMixin
from juntagrico.entity.contact import Contact, MemberContact, EmailContact, PhoneContact, TextContact
from juntagrico.entity.member import Member


class ContactInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # handle extra kwarg
        self.area = kwargs.pop('area')
        super().__init__(*args, **kwargs)


class MemberContactInlineForm(ContactInlineForm):
    def __init__(self, *args, **kwargs):
        # If user can't view members, limit options to members that are coordinators of that area
        super().__init__(*args, **kwargs)
        if not isinstance(self.fields["member"].widget, ForeignKeyRawIdWidget):
            qs = self.area.coordinators.all()
            if self.instance.id:
                qs = (qs | Member.objects.filter(pk=self.instance.member.pk)).distinct()
            self.fields["member"].queryset = qs


class ContactInline(AreaCoordinatorInlineMixin, GenericStackedPolymorphicInline):
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

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # pass parent objects area into formset
        formset.get_form_kwargs = lambda s, i: {'area': self.get_area(obj)}
        return formset
