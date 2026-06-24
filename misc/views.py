import secrets

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import BoardPost, Inquiry
from .serializers import (
    BoardPostSerializer,
    InquiryEmailSerializer,
    InquirySerializer,
    InquirySubmitSerializer,
    InquiryTokenSerializer,
)


class BoardPostViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """Public read API for the notice board (お知らせ掲示板).

    Only authenticated distributors may create posts, and a post may only be
    deleted by the user who created it.
    """

    queryset = BoardPost.objects.filter(is_active=True)
    serializer_class = BoardPostSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        profile = getattr(self.request.user, "profile", None)
        if profile is None or profile.role != "distributor":
            raise PermissionDenied("配布者のみ投稿できます")
        serializer.save(
            created_by=self.request.user,
            posted_date=timezone.localdate(),
        )

    def perform_destroy(self, instance):
        if instance.created_by_id != self.request.user.id:
            raise PermissionDenied("投稿者のみ削除できます")
        instance.delete()


class InquiryViewSet(viewsets.ModelViewSet):
    """API for the public inquiry flow.

    The flow mirrors the user registration email verification:
      1. ``send-verification-email`` creates an unverified ``Inquiry`` row with a
         token and emails the user a link to ``/inq_form?token=...``.
      2. ``verify-token`` validates the token (used by the ``/inq_form`` page).
      3. ``submit`` saves the subject/content/photo against the verified row.
    """

    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=False, methods=["post"], url_path="send-verification-email")
    def send_verification_email(self, request):
        serializer = InquiryEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        token = secrets.token_urlsafe(32)

        inquiry = Inquiry.objects.create(email=email, verification_token=token)

        try:
            verification_url = f"{settings.FRONTEND_URL}/inq_form?token={token}"
            subject = "お問い合わせ内容の入力"
            message = f"""
以下のリンクをクリックしてお問い合わせ内容を入力してください：

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
        except Exception as e:
            inquiry.delete()
            return Response(
                {"error": f"Failed to send verification email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Verification email sent successfully"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="verify-token")
    def verify_token(self, request):
        serializer = InquiryTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            inquiry = Inquiry.objects.get(verification_token=token)
        except Inquiry.DoesNotExist:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        if inquiry.is_submitted:
            return Response(
                {"error": "This inquiry has already been submitted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"email": inquiry.email}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="submit")
    def submit(self, request):
        token = request.query_params.get("token") or request.data.get("token")
        if not token:
            return Response(
                {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            inquiry = Inquiry.objects.get(verification_token=token)
        except Inquiry.DoesNotExist:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        if inquiry.is_submitted:
            return Response(
                {"error": "This inquiry has already been submitted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = InquirySubmitSerializer(instance=inquiry, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_verified=True, is_submitted=True, verification_token=None)

        return Response(
            {"message": "Inquiry submitted successfully"},
            status=status.HTTP_201_CREATED,
        )
