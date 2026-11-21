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
        return super().send_messages(self.clean_messages(email_messages))

    def send_cleaned_messages(self, email_messages):
        return super().send_messages(email_messages)

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
        bare_from_email = extract_email(message.from_email)
        if not re.match(Config.from_filter('filter_expression'), bare_from_email):
            reply_to = message.reply_to or [message.from_email]
            message.from_email = message.from_email.replace(bare_from_email, Config.from_filter('replacement_from'))
            message.reply_to = reply_to


class EmailBackend(BaseEmailBackend, smtp.EmailBackend):
    pass


class LocmemEmailBackend(BaseEmailBackend, locmem.EmailBackend):
    pass


batch_mail_sent = Signal()


class BaseBatchEmailBackend(BaseEmailBackend):
    backend = None
    batch_size = None
    split_size = None  # size of bcc slices. if 1, recipients are placed in "to" on individual emails
    wait_time = None

    def __new__(cls, *args, **kwargs):
        # backwards compatibility
        if cls.batch_size is None:
            cls.batch_size = Config.batch_mailer('batch_size')
        if cls.split_size is None:
            cls.split_size = Config.batch_mailer('batch_size')
        if cls.wait_time is None:
            cls.wait_time = Config.batch_mailer('wait_time')
        return super().__new__(cls)

    def get_backend(self):
        if self.backend is not None:
            return self.backend()
        # backward compatibility
        return super(BaseBatchEmailBackend, self)

    def send_messages(self, email_messages):
        email_messages = self.clean_messages(email_messages)
        if not email_messages:
            return 0
        # Spawn a single background thread to process all messages in the background
        t = threading.Thread(
            target=self._process_all_messages,
            args=[email_messages],
        )
        t.start()
        return len(email_messages)  # pretend that all will go well

    def open(self):
        """connections are managed internally"""
        return self

    def close(self):
        """connections are managed internally"""
        pass

    def _process_all_messages(self, email_messages):
        """Process all messages in a single thread."""
        if not email_messages:
            return

        # Step 1: Create all batches
        all_batches = list(self._create_batches(email_messages))
        if not all_batches:
            return

        # Step 2: Send each batch with wait time in between
        backend = self.get_backend()
        backend.open()
        try:
            total_batches = len(all_batches)
            for index, message_batch in enumerate(all_batches):
                backend.send_messages(message_batch)

                is_last = (index == total_batches - 1)
                batch_mail_sent.send(self.__class__, message=message_batch,
                                     original_message=email_messages, done=is_last)

                # Wait between batches (not after the last one)
                if not is_last and self.wait_time > 0:
                    backend.close()
                    time.sleep(self.wait_time)
                    backend.open()
        finally:
            backend.close()

    def _create_batches(self, email_messages):
        """Create batches from messages so each batch has ≤ batch_size recipients if possible."""
        current_batch = []
        current_count = 0
        for message in self._split_messages(email_messages):
            count = len(message.recipients())

            if current_batch and current_count + count > self.batch_size:
                yield current_batch
                current_batch = []
                current_count = 0

            current_batch.append(message)
            current_count += count

        if current_batch:
            yield current_batch

    def _split_messages(self, messages):
        """Split messages so no single message has more recipients than batch_size (if possible).

        For each message:
        - If recipients <= batch_size, yield as-is.
        - Otherwise, keep To/CC recipients in one message (without BCC),
          then create emails for BCC recipients in separate batches.
        """
        for msg in messages:
            # use default mail strategy if num of recipients is below split size or has no bcc recipients
            if not msg.bcc or len(msg.recipients()) <= self.split_size:
                yield msg
                continue

            # First send to all To and CC recipients without BCC
            if msg.to or msg.cc:
                plain_msg = copy.copy(msg)
                plain_msg.bcc = []
                yield plain_msg

            # split BCC recipients in to slices of split_size
            if msg.bcc:
                bcc_message = copy.copy(msg)
                bcc_message.to = []
                bcc_message.cc = []
                bcc_message.bcc = []
                method = 'to' if self.split_size == 1 else 'bcc'
                for i in range(0, len(msg.bcc), self.split_size):
                    new_message = copy.copy(bcc_message)
                    setattr(new_message, method, msg.bcc[i:i + self.split_size])
                    yield new_message


class BatchEmailBackend(BaseBatchEmailBackend):
    backend = smtp.EmailBackend


class ConsoleBatchEmailBackend(BaseBatchEmailBackend):
    backend = console.EmailBackend


class LocmemBatchEmailBackend(BaseBatchEmailBackend):
    backend = locmem.EmailBackend
