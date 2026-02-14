from django.contrib.sites.models import Site
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import EmailSender

"""
Form emails
"""


def contact(subject, message, member, copy_to_member):
    subject = _('Anfrage per {0}:').format(Site.objects.get_current().name) + subject
    email_sender = EmailSender.get_sender(subject, message)
    email_sender.send_to(Config.contacts('general'), reply_to=[member.email])
    if copy_to_member:
        email_sender.send_to(member.email)
