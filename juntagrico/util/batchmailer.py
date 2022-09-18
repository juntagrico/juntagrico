import copy
from django.utils import timezone
from django.conf import settings
import time
import threading


class Mailer:

    def _send_batches(msg, email_batch_size, wait_time_batch):
        tos = msg.to
        ccs = msg.cc
        bccs = msg.bcc
        num_recipients = len(bccs) + len(tos) + len(ccs)
        recipients_batches = []
        # use default mail strategy if num of recipients is below batchsize
        if num_recipients <= email_batch_size:
            msg.send()
            batch = {'timestamp': str(timezone.now()),
                     'to': tos,
                     'cc': ccs,
                     'bcc': bccs}
            recipients_batches.append(batch)
            return

        plain_msg = copy.copy(msg)
        plain_msg.bcc = []

        t_wait = 0
        # First send to all To and CC recipients without BCC
        if tos or ccs:
            starttime = time.time()
            plain_msg.send()

            plain_msg.to = []
            plain_msg.cc = []

            batch = {'timestamp': str(timezone.now()),
                     'to': tos,
                     'cc': ccs,
                     'bcc': []}
            recipients_batches.append(batch)

            t_wait = wait_time_batch - (time.time() - starttime)

        if t_wait > 0:
            time.sleep(t_wait)

        # Send BCC recipients in batches of size email_batch_size with
        # a wait time inbetween wait_time_batch
        for i in range(0, len(bccs), email_batch_size):
            starttime = time.time()
            batch_bccs = bccs[i:i + email_batch_size]

            new_message = copy.copy(plain_msg)
            new_message.bcc = batch_bccs
            new_message.send()

            batch = {'timestamp': str(timezone.now()),
                     'to': [],
                     'cc': [],
                     'bcc': batch_bccs}

            recipients_batches.append(batch)

            t_wait = wait_time_batch - (time.time() - starttime)
            if t_wait > 0:
                time.sleep(t_wait)

        send_batch_email_admin_message = \
            getattr(settings, 'EMAIL_SEND_BATCH_ADMIN_MESSAGE', False)
        # print(f'Send Admin Mail: {send_batch_email_admin_message}')

        # Send admin message to emails specified in ADMINS
        if send_batch_email_admin_message:
            Mailer._send_admin_msg(msg, recipients_batches)

    def _send_admin_msg(msg, recipients_batches):
        admin_msg = copy.copy(msg)
        admin_msg.alternatives = []
        admin_msg.cc = []
        admin_msg.bcc = []
        admin_body = ''
        for batch in recipients_batches:
            admin_body = admin_body + str(batch) + ',\n\n'
        admin_msg.body = admin_body
        admin_msg.subject = f'[JUNTAGRICO] Email Recipients: {msg.subject}'

        admins = getattr(settings, 'ADMINS', False)
        if not admins:
            return
        admin_emails = []
        for adm in admins:
            email = adm[1]
            if email is not None:
                admin_emails.append(email)

        # print('Admin Emails')
        # print(admin_emails)
        admin_msg.to = admin_emails

        admin_msg.send()

    def send(msg):

        email_batch_size = getattr(settings, 'EMAIL_BATCH_SIZE', 39)
        wait_time_batch = getattr(settings, 'EMAIL_WAIT_BETWEEN_BATCHES', 65)
        # print(f'Batch Size: {email_batch_size}')
        # print(f'Wait Time: {wait_time_batch}')

        t = threading.Thread(target=Mailer._send_batches,
                             args=[msg, email_batch_size, wait_time_batch],
                             daemon=True)
        t.start()
