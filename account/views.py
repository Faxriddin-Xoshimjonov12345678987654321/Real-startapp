from django.shortcuts import render
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import NEW, CODE_VERIFY, DONE, CustomUser
from .serializers import SignUpSerializer, VerifySerializer, LoginSerializer

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

        codes = user.codes.all().filter(code=code, used=False, expiration_time__gte = datetime.now()).first()


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

