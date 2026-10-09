from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken

from base.models import BaseModel
from shop.settings import EMAIL_EXPIRE_TIME, PHONE_EXPIRE_TIME

from datetime import timedelta, datetime
import uuid
import random
# Create your models here.


NEW, CODE_VERIFY, DONE, PHOTO_DONE = ('new', 'code_verify', 'done', 'photo_done')
VIA_PHONE, VIA_EMAIL = ('via_phone', 'via_email')
SELLER, CUSTOMER = ('seller', 'customer')


class CustomUser(AbstractUser, BaseModel):

    AUTH_STATUS = (
        (NEW, NEW), # Agart tepadagidan yani "NEW, CODE_VERIFY, DONE, PHOTO_DONE = ('new', 'code_verify', 'done', 'photo_done')" foydalanmasak unda buni ko'rinishi -> "('new', 'NEW'), ..." -> shunday qilamiz. 'new' bu bazaga saqlanishi 'NEW'bizga ko'rinishi   
        (CODE_VERIFY, CODE_VERIFY),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE)
    )

    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE),
    )

    AUTH_ROLE = (
        (SELLER, SELLER),
        (CUSTOMER, CUSTOMER)
    )

    phone_number = models.CharField(max_length=13, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=99, unique=True, blank=True, null=True)
    auth_status = models.CharField(max_length=20, choices=AUTH_STATUS, default=NEW)
    auth_type = models.CharField(max_length=120, choices=AUTH_TYPE)
    auth_role = models.CharField(max_length=20, choices=AUTH_ROLE)
    image = models.ImageField(upload_to='users/', blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.username

    def check_username(self):
        if not self.username:
            ud = str(uuid.uuid4())
            temp_username = f"username{ud[ud.rfind('-'):]}"

            while CustomUser.objects.filter(username=temp_username).exists():
                temp_username += str(random.randint(0,10))

            self.username = temp_username

    def check_pass(self):
        if not self.password:
            ud = str(uuid.uuid4())
            temp_password = f"password{ud[ud.rfind('-'):]}"
            self.password = temp_password

    def hashing_pass(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def email_normalize(self):
        if self.email:
            temp_email = self.email.lower()
            self.email = temp_email

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        
    def generate_code(self, verify_type):
        code = random.randint(1000, 9999)
        
        Verify.objects.create(
            code=code,
            user=self,
            verify_type=verify_type
        )

        return code

    def save(self, *args, **kwargs):
        self.check_username()
        self.check_pass()
        self.hashing_pass()
        self.email_normalize()
        return super().save(*args, **kwargs)


class Verify(BaseModel):
    VERIFY_TYPE = (
            (VIA_EMAIL, VIA_EMAIL),
            (VIA_PHONE, VIA_PHONE),
        )


    verify_type = models.CharField(max_length=20, choices=VERIFY_TYPE)
    used = models.BooleanField(default=False)
    expire_time = models.DateTimeField() # 12:34 12:37
    code = models.CharField(max_length=4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='codes')


    def __str__(self):
        return f"{self.user.username}---{self.code}"

    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expire_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE_TIME) # timedelte bo'lgani uchun -> 12:30 -> 12:33
        else:   
            self.expire_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE_TIME)
        super().save(*args, **kwargs)





