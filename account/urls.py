from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignUpView, VerifyView, LoginView, LogoutView, GetNewCodeView, ChangeInfoView, AddPhotoView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('code_verify/', VerifyView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('get_new_code/', GetNewCodeView.as_view(), name='get_new_code'),
    path('change_info/', ChangeInfoView.as_view(), name='change_info'),
    path('add_photo/', AddPhotoView.as_view(), name='add_photo')
    
]       