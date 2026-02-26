import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

CHARSET = "utf-8"
APP_NAME = "Date Shawarma"


def _html_wrapper(body: str, title: str | None = None) -> str:
    """Wrap plain body in a minimal HTML template for better client display."""
    title_tag = f"<title>{title}</title>" if title else ""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="{CHARSET}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {title_tag}
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .brand {{ color: #c45c26; font-weight: bold; margin-bottom: 16px; }}
        .content {{ margin: 16px 0; }}
        .footer {{ margin-top: 24px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="brand">{APP_NAME}</div>
    <div class="content">{body.replace(chr(10), "<br>")}</div>
    <div class="footer">This email was sent by {APP_NAME}. Please do not reply directly to this message.</div>
</body>
</html>"""


class EmailService:
    def __init__(self):
        self.smtp_server = settings.GOOGLE_SMTP
        self.smtp_port = settings.GOOGLE_PORT
        self.email = settings.GOOGLE_EMAIL
        self.password = settings.GOOGLE_PASSWORD

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> bool:
        """Send an email with optional HTML. Uses UTF-8 and multipart (plain + HTML) when html is provided."""
        if not self.email or not self.password:
            logger.error("SMTP credentials not configured (GOOGLE_EMAIL / GOOGLE_PASSWORD)")
            raise ValueError("Email is not configured")

        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr((APP_NAME, self.email))
        msg["To"] = to
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)

        plain_part = MIMEText(body, "plain", CHARSET)
        msg.attach(plain_part)

        if html is not None:
            html_part = MIMEText(html, "html", CHARSET)
            msg.attach(html_part)
        else:
            html_part = MIMEText(_html_wrapper(body, title=subject), "html", CHARSET)
            msg.attach(html_part)

        server = None
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            logger.debug(f"Email sent to {to}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Error sending email to {to}: {str(e)}")
            raise
        finally:
            if server is not None:
                try:
                    server.quit()
                except Exception as e:
                    logger.warning(f"SMTP quit error: {e}")
