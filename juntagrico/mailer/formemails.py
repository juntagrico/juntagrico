from django.contrib.sites.models import Site
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import EmailBuilder

"""
Form emails
"""


def contact(subject, message, member, copy_to_member):
    subject = _('Anfrage per {site}:').format(site=Site.objects.get_current().name) + ' ' + subject
    email = EmailBuilder(
        [(Config.contacts('general'), None)],
        subject,
        'mails/email.txt',
        {'content': message},
        reply_to=[member.email]
    )
    email.send()

    if copy_to_member:
        email.subject = _('[Kopie]') + ' ' + email.subject
        email.recipients = [member]
        email.reply_to = []
        email.send()
