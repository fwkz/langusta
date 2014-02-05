#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imaplib
import email


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

    def __init__(self, body):
        self.body = body

    @property
    def date(self):
        """ Get email message date """
        return self.body.get("date")

    @property
    def subject(self):
        """ Get email message date """
        return self.body.get("Subject")

    @property
    def content(self):
        """ Get email message content """
        for part in self.body.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload()

    @property
    def raw_body(self):
        return self.body

    def __str__(self):
        return "<Email Object: {}>".format(self.subject)