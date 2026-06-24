from rest_framework import serializers

from .models import BoardPost, Inquiry


class BoardPostSerializer(serializers.ModelSerializer):
    date_display = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = BoardPost
        fields = [
            "id",
            "posted_date",
            "date_display",
            "content",
            "created_by",
            "author_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "posted_date",
            "date_display",
            "created_by",
            "author_name",
            "created_at",
        ]

    def get_date_display(self, obj):
        return f"{obj.posted_date.year}年{obj.posted_date.month:02d}月{obj.posted_date.day:02d}日"

    def get_author_name(self, obj):
        if obj.created_by_id:
            profile = getattr(obj.created_by, "profile", None)
            if profile is not None:
                return profile.full_name
        return None


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
