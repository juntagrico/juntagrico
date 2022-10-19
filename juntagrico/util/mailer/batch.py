import copy

from django.core import mail
from django.dispatch import Signal
import time
import threading

from juntagrico.config import Config

batch_mail_sent = Signal()


class Mailer:
    @staticmethod
    def send(msg):
        t = threading.Thread(
            target=Mailer._send_batches,
            args=[msg, Config.batch_mailer('batch_size'), Config.batch_mailer('wait_time')],
            daemon=True
        )
        t.start()

    @staticmethod
    def _send_batches(msg, batch_size, wait_time):
        # use default mail strategy if num of recipients is below batch size
        if len(msg.recipients()) <= batch_size:
            msg.send()
            return

        # First send to all To and CC recipients without BCC
        messages = []
        if msg.to or msg.cc:
            plain_msg = copy.copy(msg)
            plain_msg.bcc = []
            messages.append(plain_msg)

        # Send BCC recipients in batches of size email_batch_size
        if msg.bcc:
            bcc_message = copy.copy(msg)
            bcc_message.to = []
            bcc_message.cc = []
            bcc_message.bcc = []
            method = 'to' if batch_size == 1 else 'bcc'  # if emails are sent out individually, receiver can be explicit
            for i in range(0, len(msg.bcc), batch_size):
                new_message = copy.copy(bcc_message)
                setattr(new_message, method, msg.bcc[i:i + batch_size])
                messages.append(new_message)

        # send emails in batches with a wait time in between
        connection = mail.get_connection()
        connection.open()  # use a single connection if there is no wait time
        for message in messages:
            start_time = time.time()
            message.connection = connection
            message.send()

            batch_mail_sent.send(Mailer, message=message, original_message=msg, done=message is messages[-1])

            t_wait = wait_time - (time.time() - start_time)
            if t_wait > 0:
                connection.close()
                time.sleep(t_wait)
                connection.open()
        connection.close()
