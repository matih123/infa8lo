import smtplib
from unidecode import unidecode
from email.utils import formatdate
from email.mime.text import MIMEText

# email = Email(sender, password, server, author_email, author_domain)
# email.send(receiver, subject, text)

class Email:
    # Constructor
    def __init__(self, sender, password, server, author_email, author_domain):
        self.sender = sender
        self.password = password
        self.server = server
        self.author_email = author_email
        self.author_domain = author_domain

    # Send email
    def send(self, receiver, subject, text):
        # Message structure
        message = f"Autor: {self.author_email}\nWysłano ze strony: {self.author_domain}\n\n{text}"
        message = MIMEText(message)

        message['Subject'] = subject
        message['From'] = f"<{self.author_email}>"
        message['To'] = receiver
        message['Date'] = formatdate(localtime=True)

        # Open connection with server
        with smtplib.SMTP_SSL(self.server, 465) as server:
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receiver, unidecode(str(message)))
