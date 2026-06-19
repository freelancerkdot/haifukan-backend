from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "auth_user"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("client", "Client"),
        ("distributor", "Distributor"),
        ("author", "Author"),
        ("manager", "Manager"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    invitation_code = models.CharField(max_length=100, blank=True, null=True)
    agreed_to_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_user_profile"

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"
