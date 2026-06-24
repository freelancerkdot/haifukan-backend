from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile
from .serializers import (
    SendVerificationEmailSerializer,
    VerifyTokenSerializer,
    CompleteRegistrationSerializer,
    LoginSerializer,
    UserProfileSerializer,
)
import secrets


@api_view(["POST"])
@permission_classes([AllowAny])
def send_verification_email(request):
    serializer = SendVerificationEmailSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        token = secrets.token_urlsafe(32)

        try:
            user = User.objects.create_user(
                username=email.split("@")[0],
                email=email,
                email_verification_token=token,
                is_active=False,
            )

            verification_url = f"{settings.FRONTEND_URL}/confirm?token={token}"
            subject = "メールアドレス確認"
            message = f"""
以下のリンクをクリックして登録を完了してください：

{verification_url}

このリンクは24時間有効です。
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response(
                {"message": "Verification email sent successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            # If user creation or email sending fails, delete the user if created
            if 'user' in locals():
                user.delete()
            return Response(
                {"error": f"Failed to send verification email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_token(request):
    serializer = VerifyTokenSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data["token"]
        return Response(
            {"message": "Token is valid", "email": User.objects.get(email_verification_token=token).email},
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def complete_registration(request):
    token = request.query_params.get("token")
    if not token:
        return Response(
            {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email_verification_token=token)
        if user.is_email_verified:
            return Response(
                {"error": "This token has already been used"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CompleteRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        password = data.pop("password")
        data.pop("confirm_password")

        user.set_password(password)
        user.is_email_verified = True
        user.is_active = True
        user.email_verification_token = None
        user.save()

        UserProfile.objects.create(user=user, **data)

        return Response(
            {"message": "Registration completed successfully"}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=email, password=password)
        if user:
            if not user.is_email_verified:
                return Response(
                    {"error": "Email address is not verified"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserProfileSerializer(user.profile).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request, user_id):
    try:
        profile = UserProfile.objects.select_related("user").get(user__id=user_id)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": "Logout failed"}, status=status.HTTP_400_BAD_REQUEST
        )
