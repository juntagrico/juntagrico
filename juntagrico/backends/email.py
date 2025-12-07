import copy
import logging
import re
import threading
import time

from django.conf import settings
from django.core.mail.backends import smtp, base, console, locmem
from django.dispatch import Signal

from juntagrico.config import Config


log = logging.getLogger('juntagrico.backends.email')


def extract_email(contact):
    # extract emails from recipients or sender that may have the form "Name <email>"
    if '<' in contact:
        return contact.split('<')[1].split('>')[0].strip()
    return contact.strip()


class BaseEmailBackend(base.BaseEmailBackend):
    golist_setting = 'WHITELIST_EMAILS'

    def send_messages(self, email_messages):
        super().send_messages(self.clean_messages(email_messages))

    def send_cleaned_messages(self, email_messages):
        super().send_messages(email_messages)

    def clean_messages(self, email_messages):
        cleaned_messages = []
        for message in email_messages:
            # only send to golisted emails when debugging
            message.to = self._filter_emails(message.to)
            message.cc = self._filter_emails(message.cc)
            message.bcc = self._filter_emails(message.bcc)
            if not message.recipients():
                continue
            # only send from email that the mailbox allows
            self.apply_from_filter(message)
            log.info('Sending email to ' + ', '.join(message.recipients()))
            cleaned_messages.append(message)
        return cleaned_messages

    def _filter_emails(self, to_emails):
        if not settings.DEBUG:
            return to_emails
        # when debugging only send to golisted emails
        passed = []
        failed = []
        go_list = getattr(settings, self.golist_setting)
        for to_email in to_emails:
            email = extract_email(to_email)
            if any(re.match(pattern, email) for pattern in go_list):
                passed.append(to_email)
            else:
                failed.append(to_email)
        if failed:
            log.info('Not sending emails in debug mode to: ' + ', '.join(failed))
        return passed

    def apply_from_filter(self, message):
        if not re.match(Config.from_filter('filter_expression'), extract_email(message.from_email)):
            reply_to = message.reply_to or [message.from_email]
            message.from_email = Config.from_filter('replacement_from')
            message.reply_to = reply_to


class EmailBackend(BaseEmailBackend, smtp.EmailBackend):
    pass


batch_mail_sent = Signal()


class BaseBatchEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        email_messages = self.clean_messages(email_messages)
        for email_message in email_messages:
            # open daemon thread that sends the emails in the background
            t = threading.Thread(
                target=self._send_batches,
                args=[email_message, Config.batch_mailer('batch_size'), Config.batch_mailer('wait_time')],
                daemon=True
            )
            t.start()
        return len(email_messages)  # pretend that all will go well

    def _send_batches(self, msg, batch_size, wait_time):
        # use default mail strategy if num of recipients is below batch size
        if len(msg.recipients()) <= batch_size:
            self.send_cleaned_messages([msg])
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
        self.open()  # use a single connection if there is no wait time
        for message in messages:
            start_time = time.time()
            message.connection = self
            self.send_cleaned_messages([message])

            batch_mail_sent.send(self.__class__, message=message, original_message=msg, done=message is messages[-1])

            t_wait = wait_time - (time.time() - start_time)
            if t_wait > 0:
                self.close()
                time.sleep(t_wait)
                self.open()
        self.close()


class BatchEmailBackend(BaseBatchEmailBackend, smtp.EmailBackend):
    pass


class ConsoleBatchEmailBackend(BaseBatchEmailBackend, console.EmailBackend):
    pass


class LocmemBatchEmailBackend(BaseBatchEmailBackend, locmem.EmailBackend):
    pass
