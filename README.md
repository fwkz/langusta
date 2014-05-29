Langusta
========

Simple package for retrieving emails from IMAP servers. Higher abstraction level built on top of Python standard library. Langusta introduce extended Email object for easier email parsing.

Getting started
---
Retrieve latest email from GMail mailbox.

```python
import langusta


SECRET_PASSWORD = "!@#$%^"
SECRET_LOGIN = "your_login"

mailbox = langusta.Mailbox(server="imap.gmail.com",
                           login=SECRET_LOGIN,
                           password=SECRET_PASSWORD)

latest_message_id = mailbox.get_message_list()[-1]

email = mailbox.get_message(latest_message_id)


print "From: {0}\nTo: {1}\nSubject: {2}\nDate: {3}\n\n {4}".format(email.sender().address, 
                                                                   email.recipient().address,
                                                                   email.date(),
                                                                   email.content())
```

License
---
MIT
