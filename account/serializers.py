from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime
from base.utils import send_email_code, email_phone_regex, validate_username

from .models import CustomUser, VIA_EMAIL, VIA_PHONE, DONE, CODE_VERIFY, NEW, PHOTO_DONE

from base.utils import email_phone_regex


class SignUpSerializer(serializers.ModelSerializer):
    email_or_phone_number = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'auth_type', 'auth_status', 'email_or_phone_number']
        read_only_fields = ['id', 'auth_type', 'auth_status']

    def validate_username(self, value):
        return validate_username(value)


    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.save()

        if user.auth_type == VIA_EMAIL:
            code = user.generate_code(user.auth_type)
            print(f"EMAIL CODE: {code}")
            #send_mail(user.email, code)

            is_sent = send_email_code(user.email, code)
            if not is_sent:
                raise ValidationError("Tasdiqlash kodini yuborishda xatolik yuz berdi Emailni tekshiring")

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
                self.send_code_check(user)
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

    def send_code_check(self, user):
        codes = user.codes.all().filter(used=False, expire_time__gte=datetime.now()).first()
        if codes:
            raise ValidationError('Sizda hali aktiv kod bor')
        
        return True



class ChangeInfoSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'auth_status', 'auth_type', 'first_name', 'last_name', 'username', 'password', 'confirm_password']
        read_only_fields = ['id', 'auth_status', 'auth_type']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise ValidationError('Parol mos emas')

        return attrs


    def update(self, instance, validated_data):
        if instance.auth_staus != CODE_VERIFY:
            raise ValidationError('Siz toliq royxatdan otmagansiz')

        # if validated_data['first_name']: PATCH ....
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.username = validated_data.get('username')
        instance.password = instance.set_password(validated_data.get('username'))

        instance.auth_status = DONE
        instance.save()

        return instance





class AddPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_status', 'auth_type', 'first_name', 'last_name', 'username', 'image']
        read_only_fields = ['id', 'auth_status', 'auth_type', 'first_name', 'last_name', 'username']

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise ValidationError('Parol mos emas')

        return attrs


    def update(self, instance, validated_data):
        if instance.auth_status != DONE:
            raise ValidationError('Siz toliq royxatdan otmagansiz')

        image = validated_data.get('image')
        if image:
            instance.image = image
                    
            instance.auth_status = PHOTO_DONE
            instance.save()
        
        return instance






class VerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4, required=True)


class LoginSerializer(serializers.Serializer):
    email_or_phone_number = serializers.CharField(required=True)

    def validate(self, attrs):
        user_input = attrs.get('email_or_phone_number')

        user = CustomUser.objects.filter(Q(phone_number=user_input) | Q(email=user_input)).first()


        if not user:
            raise ValidationError({
                "error": "Bunday foydalanuvchi topilmadi!"
            })

        attrs['user'] = user
        return attrs

