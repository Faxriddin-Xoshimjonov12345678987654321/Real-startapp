from django.shortcuts import render
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from base.utils import send_email_code
from .models import NEW, CODE_VERIFY, DONE, CustomUser, VIA_EMAIL, VIA_PHONE
from .serializers import SignUpSerializer, VerifySerializer, LoginSerializer, ChangeInfoSerializer, AddPhotoSerializer

from datetime import datetime
# Create your views here.

# request.user.auth_status = NEW -> Agar tepadan import qilamsak bundau ishlataolmaymiz 

class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
    queryset = CustomUser.objects.all()


class VerifyView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VerifySerializer
    queryset = CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        #Kelgan ma'lumotni serailizer orqali tekshiramiz (code 4 xonali  va majburiy ekanligini tekshiradi)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        code = request.data.get('code')
        user = request.user

        codes = user.codes.all().filter(code=code, used=False, expire_time__gte = datetime.now()).first()
        print(codes, '---------------------------------------')
        if codes is None:
            raise ValidationError('Kod eskirgan yoki yaroqsiz')

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFY
            codes.used = True

            user.save()
            codes.save()

        return Response({
            'message': 'kod tasdiqlandi',
            'auth_status': user.auth_status
        })


        if not codes:
            return Response({
                "error": "Tasdiqlash kodi xato yoki muddati o'tgan!"
            }, status=status.HTTP_400_BAD_REQUEST)

        codes.used = True
        codes.save()


        if user.auth_status == NEW:
            user.auth_status == DONE
            user.save()

        return Response({
            "message": "Hisobingiz muffaqiyatli tasdiqlandi!",
            "token": user.token()
        }, status=status.HTTP_200_OK)


class GetNewCodeView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.auth_status != NEW:
            raise ValidationError('Sizda bu xolat taqiqlangan')

        codes = user.codes.all().filter(used=False, expire_time__gte = datetime.now()).first()
        if codes:
            raise ValidationError('Sizda hali aktiv kod bor. Keyinroq urinib koring')


        # if 


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

        return Response({
            'message': 'Kod yuborildi'
        })
        


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    queryset = CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(date=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')

        return Response({
            "message": "Muffaqiyatli kirish!",
            "token": user.token(),
            "auth_status": user.auth_status
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({
                    "error": "Refresh token talab qilinadi!"
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "message": "Muvaffaqiyatili chiqildi!"
            }, status=status.HTTP_200_OK)

        except Exception as error:
            return Response({
                "error": "Xatolik yuz berdi yoki token yaroqsiz"
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangeInfoView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangeInfoSerializer
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user


class AddPhotoView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddPhotoSerializer
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user

