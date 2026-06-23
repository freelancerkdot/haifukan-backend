from rest_framework import serializers

from .models import Inquiry


class InquiryEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class InquiryTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class InquirySubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["subject", "content", "photo"]

    def validate_subject(self, value):
        if not value:
            raise serializers.ValidationError("件名を選択してください")
        return value

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("内容を入力してください")
        return value


class InquirySerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source="get_subject_display", read_only=True)

    class Meta:
        model = Inquiry
        fields = [
            "id",
            "email",
            "subject",
            "subject_display",
            "content",
            "photo",
            "is_verified",
            "is_submitted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
