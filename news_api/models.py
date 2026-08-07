from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class User(AbstractUser):
    ROLES_CHOICES = (
    ("reader", "Reader"),
    ("editor", "Editor"),
    ("journalist", "Journalist"),
    )
    role = models.CharField(
        max_length=20, choices=ROLES_CHOICES, default="reader"
    )

    #Reader fields
    subscribed_publishers = models.ManyToManyField(
        "Publisher", blank=True, related_name="subscribers"
    )
    subscribed_journalists = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="subscribers"
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        #Assign user to corresponding group on vreation/update
        group, _ = Group.objects.get_or_create(name=self.role.capitalize())
        self.groups.clear()
        self.groups.add(group)

        #set reader fields to none/clear if not a reader
        if self.role != "reader":
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()

class Publisher(models.Model):
    name = models.CharField(max_length=255)
    editors = models.ManyToManyField(
        User, limit_choices_to={"role": "editors"}, related_name="publishers"
    )
    journalists = models.ManyToManyField(
        User,
        limit_choices_to={"role": "journalist"},
        related_name="associated_publishers",
    )

    def __str__(self):
        return self.name
    
class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "journalist"},
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
        return self.title

class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "journalist"},
        related_name="newsletter",
    )
    articles = models.ManyToManyField(Article, related_name="newsletters")

    def __str__(self):
        return self.title