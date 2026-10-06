from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from base.utils import send_email_code

from .models import CustomUser, VIA_EMAIL, VIA_PHONE, DONE, CODE_VERIFY, NEW, PHOTO_DONE

from base.utils import email_phone_regex


class SignUpSerializer(serializers.ModelSerializer):
    email_or_phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_type', 'auth_status', 'email_or_phone_number']
        read_only_fields = ['id', 'auth_type', 'auth_status']


    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.save()

        if user.auth_type == VIA_EMAIL:
            code = user.generate_code(user.auth_type)
            print(f"EMAIL CODE: {code}")
            #send_mail(user.email, code)

            send_email_code(user.email, code)

        elif user.auth_type == VIA_PHONE:
            code = user.generate_code(user.auth_type)
            print(f"PHONE NUMBER CODE: {code}")
            #send_SMS(user.phone_number, code)


        else:
             raise ValidationError('Email yoki telefon raqam xato kiritilgan')

        return user


    def to_representation(self, instance):
        data = super().to_representation(instance)

        return {
            'token': instance.token(),
            'data': data
        }



    def validate(self, attrs):

        user_input = attrs.get('email_or_phone_number')

        user = CustomUser.objects.filter(Q(phone_number=user_input) | Q(email=user_input)).first()

        if user:
            if user.auth_status in [DONE, PHOTO_DONE]:
                raise ValidationError('email yoki telefon raqamingiz bizdan oldin royxatdan otgan') 
            else:
                user.delete()



        user_input_tupe = email_phone_regex(user_input)

        if user_input_tupe == 'email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }

        elif user_input_tupe == 'phone':
            data = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE
            }

        else:
            raise ValidationError('Siz xato email yoki telefon raqam kiridingiz')

        return data