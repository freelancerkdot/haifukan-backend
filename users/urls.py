from django.urls import path
from .views import (
    send_verification_email,
    verify_token,
    complete_registration,
    login,
    profile,
    user_info,
    logout,
)

urlpatterns = [
    path("send-verification-email/", send_verification_email, name="send_verification_email"),
    path("verify-token/", verify_token, name="verify_token"),
    path("complete-registration/", complete_registration, name="complete_registration"),
    path("login/", login, name="login"),
    path("profile/", profile, name="profile"),
    path("user-info/<uuid:user_id>/", user_info, name="user_info"),
    path("logout/", logout, name="logout"),
]
