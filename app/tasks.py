import os
from celery import shared_task
from smtplib import SMTP
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

CELERY_EMAIL = os.getenv('CELERY_EMAIL')
CELERY_PASSWORD = os.getenv('CELERY_PASSWORD')

@shared_task
def send_welcome_email(email: str):
    message = EmailMessage()
    message["From"] = CELERY_EMAIL
    message["To"] = email
    message["Subject"] = "Welcome to My App"
    message.set_content("Thank you for registering!")

    with SMTP(host="smtp.gmail.com", port=587) as server:
        server.starttls()
        server.login(CELERY_EMAIL, CELERY_PASSWORD)
        server.send_message(message)
