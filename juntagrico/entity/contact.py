from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.html import urlize
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.entity import JuntagricoBasePoly
from juntagrico.entity.member import Member


def get_emails(source, fallback, get_member, exclude):
    email_contacts = source.filter(
        Q(instance_of=EmailContact) | Q(MemberContact___display__in=[MemberContact.DISPLAY_EMAIL,
                                                                     MemberContact.DISPLAY_EMAIL_TEL])
    )
    # if there are email contacts return all their emails except for excludes, otherwise use the fallback
    if email_contacts.count():
        exclude = exclude or []
        result = []
        for contact in email_contacts:
            if contact.email not in exclude:
                # if `get_members` is true, also return the member object (if available)
                if get_member:
                    result.append((contact.email, getattr(contact, 'member', None)))
                else:
                    result.append(contact.email)
        return result
    return fallback(get_member, exclude)


class Contact(JuntagricoBasePoly):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.BigIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    sort_order = models.PositiveIntegerField(_('Reihenfolge'), default=0, blank=False, null=False)

    def to_html(self):
        return mark_safe('<span class="contact contact-{}">{}</span>'.format(
            self.__class__.__name__.lower().replace('contact', ''),
            self._inner_html()
        ))

    def _inner_html(self):
        raise NotImplementedError

    class Meta:
        verbose_name = _('Kontakt')
        verbose_name_plural = _('Kontakte')
        ordering = ['sort_order']


class MemberContact(Contact):
    DISPLAY_EMAIL = 'E'
    DISPLAY_TEL = 'T'
    DISPLAY_EMAIL_TEL = 'B'
    DISPLAY_OPTIONS = [
        (DISPLAY_EMAIL, _('E-Mail')),
        (DISPLAY_TEL, _('Telefonnummer')),
        (DISPLAY_EMAIL_TEL, _('E-Mail & Telefonnummer')),
    ]

    member = models.ForeignKey(Member, on_delete=models.PROTECT, verbose_name=Config.vocabulary('member'))
    display = models.CharField(_('Anzeige'), max_length=1, choices=DISPLAY_OPTIONS, default=DISPLAY_EMAIL)

    @property
    def show_email(self):
        return self.display in [self.DISPLAY_EMAIL, self.DISPLAY_EMAIL_TEL]

    @property
    def show_tel(self):
        return self.display in [self.DISPLAY_TEL, self.DISPLAY_EMAIL_TEL]

    def __str__(self):
        strings = [str(self.member)]
        if self.show_email:
            strings.append(self.member.email)
        if self.show_tel:
            if self.member.mobile_phone:
                strings.append(self.member.mobile_phone + ',')
            strings.append(self.member.phone)
        return " ".join(strings)

    @property
    def email(self):
        if self.show_email:
            return self.member.email
        return None

    def _inner_html(self):
        inner_html = '<span class="contact-member-name">{}</span>\n'.format(self.member)
        if self.show_email:
            inner_html += '<span class="contact-member-email"><a href="mailto:{0}">{0}</a>' \
                          '</span>\n'.format(self.member.email)
        if self.show_tel:
            if self.member.mobile_phone:
                inner_html += '<span class="contact-member-mobile-phone">{}</span>\n'.format(self.member.mobile_phone)
            inner_html += '<span class="contact-member-phone">{}</span>\n'.format(self.member.phone)
        return inner_html

    def copy(self):
        return MemberContact(member=self.member, display=self.display)

    class Meta:
        verbose_name = Config.vocabulary('member')
        verbose_name_plural = Config.vocabulary('member_pl')


class EmailContact(Contact):
    email = models.EmailField(_('E-Mail'))

    def __str__(self):
        return self.email

    def _inner_html(self):
        return '<a href="mailto:{0}">{0}</a>'.format(self.email)

    def copy(self):
        return EmailContact(email=self.email)

    class Meta:
        verbose_name = _('E-Mail-Adresse')
        verbose_name_plural = _('E-Mail-Adresse')


class PhoneContact(Contact):
    phone = models.CharField(_('Telefonnummer'), max_length=50)

    def __str__(self):
        return self.phone

    def _inner_html(self):
        return self.phone

    def copy(self):
        return PhoneContact(phone=self.phone)

    class Meta:
        verbose_name = _('Telefonnummer')
        verbose_name_plural = _('Telefonnummer')


class TextContact(Contact):
    text = models.TextField(_('Kontaktbeschrieb'))

    def __str__(self):
        return self.text

    def _inner_html(self):
        return urlize(self.text)

    def copy(self):
        return TextContact(text=self.text)

    class Meta:
        verbose_name = _('Freier Kontaktbeschrieb')
        verbose_name_plural = _('Freie Kontaktbeschriebe')
