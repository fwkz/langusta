#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imaplib
import email


class SuperEmail(object):
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

    def get_message_date(self, email_id):
        """ Get email message date

            Args:
            email_id - ID of email.

            Return email date in STRING.
        """
        email_message = self.__get_message(email_id)
        date = self.__get_data("date", email_message)
        return date

    def get_message_content(self, email_id):
        """ Get email message content

            Args:
            email_id - ID of email.

            Return email content in STRING.
        """
        email_message = self.__get_message(email_id)
        content = self.__get_data("content", email_message)
        return content

    def __get_data(self, data, email_message):
        for part in email_message.walk():
            part_content_type = part.get_content_type()
            if part_content_type == "multipart/related" and data == "date":
                return part["date"]
            elif part_content_type == 'text/plain' and data == "content":
                return part.get_payload()

    def __get_message(self, email_id):
        result, data = self.mailbox.fetch(email_id, "(RFC822)")  # fetch the email body (RFC822) for the given ID
        raw_email = data[0][1]  # body, which is raw text of the email including headers and alternate payloads
        email_message = email.message_from_string(raw_email)
        return email_message