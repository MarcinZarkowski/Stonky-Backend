import random 
import string
import environ
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import os

def send_mail(user, subject):
    documents={'Verify email for Stonky':'verify_email_message.html', 'Stonky password reset':'reset_password_message.html'}
    

    def get_random_string(length):
        characters = string.ascii_letters + string.digits
        token = ''.join(random.choice(characters) for i in range(length))
        return token

    
    token = get_random_string(length=32)


    from_email = settings.EMAIL_HOST_USER
    FRONTEND_URL = os.environ.get('FRONTEND_URL')

    recipient_list = [user.email]
    context = {
        'user.name': user.username,
        'frontend_url': FRONTEND_URL+"/",
        'token':token,
    }
    message = render_to_string(documents[subject], context)
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.content_subtype = 'html'  # Important to send as HTML
    email.send()
    
    return token

    

