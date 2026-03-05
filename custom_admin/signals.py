from django.db.models.signals import post_save
from django.dispatch import receiver
from portfolio.models import ContactMessage
import sys

@receiver(post_save, sender=ContactMessage)
def notify_new_message(sender, instance, created, **kwargs):
    """Print notification when new message is received"""
    if created:
        print("\n" + "="*60)
        print("🚨 NEW CONTACT MESSAGE RECEIVED!")
        print("="*60)
        print(f"From: {instance.name} <{instance.email}>")
        print(f"Subject: {instance.subject}")
        print(f"Message Preview: {instance.message[:100]}...")
        print(f"Time: {instance.submitted_at}")
        print("="*60 + "\n")
        sys.stdout.flush()