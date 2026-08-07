from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests 
from .models import Article

@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, updated_fields, **kwargs):
    #Only act if article is approved
    if instance.approved:
        emails = set()
        if instance.publisher:
            emails.update(
                instance.publisher.subscribes.value_list("email", flat=True)
            )
        if instance.author:
            emails.update(
                instance.author.subscribers.value_list("email", flat=True)
            )

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