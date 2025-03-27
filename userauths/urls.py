from django.urls import path, include
from rest_framework import routers
from userauths import views
from userauths.views import (
    UserRegisterView,
    UserLoginView,
    #UserLogoutView,
    LogoutView,
    ProfileUpdateView,
    ContactUsView,
)

router = routers.DefaultRouter()


app_name = "userauths"

urlpatterns = [
    # API URLs first
    path('api/register/', UserRegisterView.as_view(), name='user-register'),
    path('api/login/', UserLoginView.as_view(), name='user-login'),
    path('api/profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    #path("api/logout/", UserLogoutView.as_view(), name="user-logout"),  
    path("logout/", LogoutView.as_view(), name="logout"),
    path('api/contact/', ContactUsView.as_view(), name='contact-us'),
    path('api/', include(router.urls)),  


    # HTML Front View URLs
    path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),
    path("profile/update/", views.profile_update, name="profile-update"),
]