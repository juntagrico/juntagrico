from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from juntagrico.mailer import send_mail_multi

def send_politoloco_mail(subject, message, text_message, emails, server, attachments):
    plaintext = get_template('mails/politoloco.txt')
    htmly = get_template('mails/politoloco.html')

    htmld = {
        'subject': subject,
        'content': message,
        'serverurl': "http://" + server
    }
    textd = {
        'subject': subject,
        'content': text_message,
        'serverurl': "http://" + server
    }

    text_content = plaintext.render(textd)
    html_content = htmly.render(htmld)

    msg = EmailMultiAlternatives(subject, text_content, 'info@ortoloco.ch', emails)
    msg.attach_alternative(html_content, "text/html")
    for attachment in attachments:
        msg.attach(attachment.name, attachment.read())
    send_mail_multi(msg)