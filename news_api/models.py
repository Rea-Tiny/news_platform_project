"""Database models for the news_api application."""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# Create your models here.
class CustomUser(AbstractUser):
    """Custom user models extending AbstactUser with roles
    and publisher assignments."""

    ROLES_CHOICES = (
        ("reader", "Reader"),
        ("editor", "Editor"),
        ("journalist", "Journalist"),
    )
    role = models.CharField(
        max_length=20, choices=ROLES_CHOICES, default="reader"
    )
    email = models.EmailField(unique=True)

    # Reader fields
    subscribed_publishers = models.ManyToManyField(
        "Publisher", blank=True, related_name="subscribers"
    )
    subscribed_journalists = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="subscribers"
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Assign user to corresponding group on vreation/update
        group, _ = Group.objects.get_or_create(name=self.role.capitalize())
        self.groups.clear()
        self.groups.add(group)

        # Clear reader fields if role is not a reader
        if self.role != "reader":
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()


class Publisher(models.Model):
    """Model representing a news publishing entity."""
    name = models.CharField(max_length=255)
    editors = models.ManyToManyField(
        CustomUser, limit_choices_to={"role": "editors"},
        related_name="edited_publishers", blank=True
    )
    journalists = models.ManyToManyField(
        CustomUser,
        related_name="assigned_publishers", blank=True
    )

    def __str__(self):
        """Return publisher name."""
        return self.name


class Article(models.Model):
    """Model representing an individual news article."""
    title = models.CharField(max_length=255)
    content = models.TextField()
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="articles"
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        """Return article title."""
        return self.title


class Newsletter(models.Model):
    """Model representing a newsletter containing a
    curated collection of articles."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="newsletters",
    )
    articles = models.ManyToManyField(Article, related_name="newsletters")

    def __str__(self):
        """Return newsletter title."""
        return self.title
