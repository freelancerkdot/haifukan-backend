from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile
import secrets


class SendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already registered")
        return value


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            user = User.objects.get(email_verification_token=value)
            if user.is_email_verified:
                raise serializers.ValidationError("This token has already been used")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid token")


class CompleteRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "role",
            "company_name",
            "full_name",
            "postal_code",
            "address",
            "phone_number",
            "invitation_code",
            "agreed_to_terms",
            "password",
            "confirm_password",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        if not attrs["agreed_to_terms"]:
            raise serializers.ValidationError(
                {"agreed_to_terms": "You must agree to the terms of service"}
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "is_email_verified"]
        read_only_fields = ["id", "is_email_verified"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "registration_number",
            "role",
            "company_name",
            "full_name",
            "postal_code",
            "address",
            "phone_number",
            "invitation_code",
            "agreed_to_terms",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
