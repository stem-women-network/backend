import smtplib
import ssl
from email.message import EmailMessage

from pydantic import EmailStr

import dotenv
import os

dotenv.load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
SMTP_PROVIDER = os.getenv("SMTP_PROVIDER", "")
SMTP_PORT = os.getenv("SMTP_PORT", "")

class EmailService:
    @staticmethod
    def send_coordinator_invite(coordinator_email : EmailStr, temp_password: str, university_name : str):
        msg = EmailMessage()
        msg.set_content(
            f"""
            Nome da instituição: {university_name}
            Senha Temporária: {temp_password}
            """
        )
        msg['Subject'] = 'Convite de Coordenador'
        msg['From'] = ''
        msg['To'] = coordinator_email
        try:
            # Create a secure SSL context
            context = ssl.create_default_context()

            # Connect to the Gmail SMTP server and login
            with smtplib.SMTP_SSL(SMTP_PROVIDER, int(SMTP_PORT), context=context) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, coordinator_email, msg.as_string())
                print("Email sent successfully!")

        except smtplib.SMTPAuthenticationError:
            print("Authentication failed. Check your email and App Password.")
        except Exception as e:
            print(f"An error occurred: {e}")
