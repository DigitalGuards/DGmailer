from dataclasses import dataclass
from typing import Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

@dataclass
class SMTPServer:
    server: str
    port: int
    username: str
    password: str
    tls_mode: str

    def test_connection(self) -> tuple[bool, str]:
        """Test the SMTP server connection.

        Returns:
            tuple[bool, str]: A tuple containing success status and message
        """
        try:
            if self.tls_mode == 'ON / Implicit TLS':
                server = smtplib.SMTP_SSL(self.server, self.port)
            else:
                server = smtplib.SMTP(self.server, self.port)
                if self.tls_mode == 'ON / Explicit TLS':
                    server.starttls()
            
            server.login(self.username, self.password)
            server.quit()
            return True, "Connection successful!"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def send_email(self, 
                  sender_address: str,
                  sender_name: Optional[str],
                  to_email: str,
                  subject: str,
                  body: str,
                  is_html: bool = False,
                  reply_to: Optional[str] = None,
                  cc: Optional[str] = None,
                  bcc: Optional[str] = None,
                  attachment_path: Optional[str] = None) -> tuple[bool, str]:
        """Send an email through this SMTP server.

        Args:
            sender_address: The email address of the sender
            sender_name: Optional display name for the sender
            to_email: The recipient's email address
            subject: Email subject
            body: Email body content
            is_html: Whether the body is HTML formatted
            reply_to: Optional reply-to address
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            attachment_path: Optional path to attachment file

        Returns:
            tuple[bool, str]: A tuple containing success status and message
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{sender_name} <{sender_address}>" if sender_name else sender_address
            msg['To'] = to_email

            if reply_to:
                msg.add_header('Reply-To', reply_to)
            if cc:
                msg.add_header('Cc', cc)
            if bcc:
                msg.add_header('Bcc', bcc)

            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

            if attachment_path:
                with open(attachment_path, 'rb') as file:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(file.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition', 
                                       f'attachment; filename={attachment_path}')
                    msg.attach(attachment)

            if self.tls_mode == 'ON / Implicit TLS':
                server = smtplib.SMTP_SSL(self.server, self.port)
            else:
                server = smtplib.SMTP(self.server, self.port)
                if self.tls_mode == 'ON / Explicit TLS':
                    server.starttls()

            server.login(self.username, self.password)
            server.sendmail(sender_address, to_email, msg.as_string())
            server.quit()
            
            return True, "Email sent successfully"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
