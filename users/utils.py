from django.core.mail import send_mail
from django.conf import settings

def send_email(name, email):
    subject = 'Welcome to Real Estate Platform'
    body = f'''
             Hi {name}, Thank you for registering at our Real Estate Platform. Best regards, Real Estate Team.
            '''
    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    