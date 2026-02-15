import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = settings.GOOGLE_SMTP
        self.smtp_port = settings.GOOGLE_PORT
        self.email = settings.GOOGLE_EMAIL
        self.password = settings.GOOGLE_PASSWORD

    def send_email(self, to: str, subject: str, body: str):
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
