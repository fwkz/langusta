#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imaplib
import email
import datetime
import base64
from collections import namedtuple


ContentTypes = namedtuple("ContentTypes", ["HTML", "PLAINTEXT"])
content_types = ContentTypes("text/html", "text/plain")


class Mailbox(object):
    """ Class for parsing email messages.

        Args:
        server - IMAP email host
        login - user login to the mailbox
        password - user password to the mailbox
    """
    def __init__(self, server, login, password):
        self.mailbox = imaplib.IMAP4_SSL(server)
        self.mailbox.login(login, password)
        self.mailbox.select("INBOX")

    def select_folder(self, folder="INBOX"):
        """ Connect to mailbox folder """
        self.mailbox.select(folder)

    def folders(self):
        """  Return list of "folders" aka labels in GMAIL """
        return self.mailbox.list()

    def get_message_list(self, start=None, end=None, criterion='ALL'):
        """ Get list of messages

            Args:
            start - starting point
            end - ending point

            Returns list of email IDs.
         """
        result, data = self.mailbox.search(None, criterion)  # '(SUBJECT "Invitation to fill out an Equivalency Determination questionnaire")'
        ids_list = data[0].split()
        return ids_list[start:end]

    def get_message(self, email_id):
        result, data = self.mailbox.fetch(email_id, "(RFC822)")  # fetch the email body (RFC822) for the given ID
        raw_email = data[0][1]  # body, which is raw text of the email including headers and alternate payloads
        email_message = email.message_from_string(raw_email)
        return Email(email_message)


class Email(object):
    """ Wrapper for email.message.Message """

    def __init__(self, raw_body):
        self.body = email.message_from_string(raw_body)

    def date(self):
        """ Get email message DATE """
        payload = self.body.get("date")
        date_tuple = email.utils.parsedate_tz(payload)
        time_tz = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
        return time_tz

    def subject(self):
        """ Get email message SUBJECT """
        feed = self.body.get("Subject")
        decoded_subject = email.Header.decode_header(feed).pop()[0]
        return decoded_subject

    def content(self, content_type=content_types.HTML):
        """ Get email message CONTENT """
        content = None

        for part in self.body.walk():
            if part.get_content_type() == content_type:
                content = self.__decode_content(part)
        else:
            return content or False

    @staticmethod
    def __decode_content(part):
        payload = part.get_payload()
        content_transfer_encoding = part.get("content-transfer-encoding")
        if content_transfer_encoding.lower() == "quoted-printable":
            return email.quoprimime.body_decode(payload)
        elif content_transfer_encoding.lower() == "base64":
            return base64.decodestring(payload)
        else:
            return payload

    def sender(self):
        """ Get email message SENDER """
        feed = self.body.get("from")
        decoded_address = email.Header.decode_header(feed).pop()[0]
        return self.__parse_address(decoded_address)

    def recipient(self):
        """ Get email message RECIPIENT """
        feed = self.body.get("to")
        decoded_address = email.Header.decode_header(feed).pop()[0]
        return self.__parse_address(decoded_address)

    @staticmethod
    def __parse_address(raw_address):
        parsed_addr = email.utils.parseaddr(raw_address)

        EmailAddress = namedtuple("EmailAddress", "label, address, raw")
        label = email.Header.decode_header(parsed_addr[0]).pop()[0]  # Decode label
        return EmailAddress(label, parsed_addr[1], raw_address)

    def __str__(self):
        return "<Email Object: {}>".format(self.subject)