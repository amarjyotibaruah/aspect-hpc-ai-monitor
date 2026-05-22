"""Email sender for ASPECT monitoring reports."""

import os
import smtplib
from email.message import EmailMessage


class EmailSender:
    """Send monitoring reports by email."""

    def __init__(self):
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_to = os.getenv("EMAIL_TO")

        if not all([self.email_user, self.email_password, self.email_to]):
            raise ValueError(
                "Missing EMAIL_USER, EMAIL_PASSWORD, or EMAIL_TO environment variable"
            )

    def send_report(self, subject, body, report_path=None):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.email_user
        msg["To"] = self.email_to
        msg.set_content(body)

        if report_path:
            with open(report_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(report_path)

            msg.add_attachment(
                file_data,
                maintype="text",
                subtype="markdown",
                filename=file_name,
            )

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
