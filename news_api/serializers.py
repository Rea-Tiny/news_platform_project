from rest_framework import serializers
from .models import Article, Newsletter, Publisher, CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomerUser model instances."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "role",
            "subscribed_publishers",
            "subscribed_journalists",
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher model instances."""

    class Meta:
        model = Publisher
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model instances."""

    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "publisher",
            "created_at",
            "approved",
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model instance."""

    class Meta:
        model = Newsletter
        fields = "__all__"
