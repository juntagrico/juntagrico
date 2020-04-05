from django.template.loader import get_template
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import base_dict
from juntagrico.mailer.emailsender import prepare_email, send_to, attach_files, attach_html, send


class FormEmails:
    """
    Form emails
    """
    @staticmethod
    def contact(subject, message, member, copy_to_member):
        subject = _('Anfrage per {0}:').format(Config.adminportal_name()) + subject
        email = prepare_email(subject, message)
        send_to(email, Config.info_email(), reply_to=member.email)
        if copy_to_member:
            send_to(email, member.email)

    @staticmethod
    def contact_member(subject, message, member, contact_member, copy_to_member, files):
        subject = _('Nachricht per {0}:').format(Config.adminportal_name()) + subject
        email =prepare_email(subject, message, reply_to=[member.email])
        attach_files(email, files)
        send_to(email, contact_member.email)
        if copy_to_member:
            send_to(email, member.email)

    @staticmethod
    def internal(subject, message, text_message, emails, files, sender):
        htmld = base_dict({
            'mail_template': Config.mail_template,
            'subject': subject,
            'content': message
        })
        textd = base_dict({
            'subject': subject,
            'content': text_message
        })
        text_content = get_template('mails/form/filtered_mail.txt').render(textd)
        html_content = get_template('mails/form/filtered_mail.html').render(htmld)
        email = prepare_email(subject, text_content, bcc=emails, from_email=sender)
        attach_html(email, html_content)
        attach_files(email, files)
        send(email)