import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")


def send_email(to: str, subject: str, html: str):
    try:
        response = resend.Emails.send({
            "from": os.getenv("EMAIL_FROM"),
            "to": to,
            "subject": subject,
            "html": html,
        })
        print("Email sent successfully:", response)
    except Exception as e:
        print("Email sending failed:", str(e))