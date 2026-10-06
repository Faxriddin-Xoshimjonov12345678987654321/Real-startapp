from django.shortcuts import render
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import permissions

from .models import NEW, CODE_VERIFY, CustomUser
from .serializers import SignUpSerializer

from datetime import datetime
# Create your views here.

# request.user.auth_status = NEW -> Agar tepadan import qilamsak bundau ishlataolmaymiz 

class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
    queryset = CustomUser.objects.all()


class VerifyView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()

    def post(self, request):
        code = request.data.get('code')
        user = request.user

        codes = user.codes.all().filter(code=code, used=False, expiration_time__gte = datetime.now()).first()
        pass
