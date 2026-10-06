from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail

import re


email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
phone_regex = re.compile(r'\+998(90|91|93|94|95|98|99|33|97|71)\d{7}$')
username_regex = re.compile(r'^[a-zA-Z0-9_]{3,20}$')


def email_phone_regex(user_input):
    if re.fullmatch(email_regex, user_input):
        return 'email'

    elif re.fullmatch(phone_regex, user_input):
        return 'phone'

    else:
        raise ValidationError('Siz xato email yoki telefon raqam kiritdingiz')


def validate_username(username):
    if not re.fullmatch(username_regex, username):
        raise ValidationError({"username": "Username faqat harflar, raqamlar va '_' dan iborat bo'lishi kerak (3-20 ta belgi)"})
    return 'username'


def send_email_code(email, code):
  subject = 'Royxatdan otish uchun tasdiqlash kodi'
  message = f'Sizning tasdiqlash kodingiz: {code}'
  email_from = settings.EMAIL_HOST_USER
  recipient_list = [email]


  try:
     send_mail(
            subject=subject, 
            message=message, 
            from_email=email_from, 
            recipient_list=recipient_list,
            fail_silently=False,
            )
     return True
  except Exception as error:
      print(f"Email yuborishda xatolik: {error}")

      return False
      

