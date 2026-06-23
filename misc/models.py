from django.db import models
import uuid


class Inquiry(models.Model):
    SUBJECT_CHOICES = [
        ("distribution_center", "配布館に関して"),
        ("posting", "ポスティングに関して"),
        ("flyer_info", "チラシ情報提供"),
        ("flyer_protest", "チラシ配布に対する抗議"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, blank=True)
    content = models.TextField(blank=True)
    photo = models.ImageField(upload_to="inquiries/", blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "misc_inquiry"
        ordering = ["-created_at"]
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"{self.email} - {self.get_subject_display() or 'pending'}"
