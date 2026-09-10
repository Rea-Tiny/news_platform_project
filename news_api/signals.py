from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests

from .models import Article


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, updated_fields, **kwargs):
    """Send email notifications when an article is approved."""
    if instance.approved:
        emails = set()

        # Collect email addresses of users subscribed to publisher
        if instance.publisher:
            publisher_emails = instance.publisher.subsribed.values_list(
                "email", flat=True
            )
            emails.update(publisher_emails)

        # Collect email addresses of users subscribed to the author
        if instance.author and hasattr(instance.author, "subscribers"):
            author_emails = instance.author.subscribers.values_list(
                "email", flat=True
            )
            emails.update(author_emails)

        recipients_list = [e for e in emails if e]
        
        if recipients_list:
            send_mail(
                subject=f"New Approved Article: {instance.title}",
                message=instance.content,
                from_email="noreply@newsapp.com",
                recipient_list=recipients_list,
                fail_silently=True,
            )

        try:
            requests.post(
                "http://127.0.0.1:8000/api/approved/",
                json={"article_id": instance.id, "title": instance.title},
                timeout=5,
            )
        except Exception:
            pass
