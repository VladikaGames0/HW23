from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UserRegistrationView, UserLoginView, UserLogoutView, ProfileView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]