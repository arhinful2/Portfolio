from django.http import JsonResponse
from portfolio.models import ContactMessage
from django.utils import timezone
import sys

def send_test_email(request, message_id):
    """Send test email for a message (prints to console)"""
    # Simple check if user is staff (without decorator)
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized'
        })
    
    try:
        message = ContactMessage.objects.get(id=message_id)
        
        print("\n" + "="*60)
        print("📧 TEST EMAIL REPLY (Quick Action):")
        print("="*60)
        print(f"To: {message.email}")
        print(f"Subject: Re: {message.subject}")
        print(f"Message: Hello {message.name},\\n\\nThank you for your message!\\n\\nBest regards,\\nAdmin")
        print("="*60 + "\n")
        sys.stdout.flush()
        
        # Update status
        message.is_read = True
        message.is_responded = True
        message.replied_at = timezone.now()
        message.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Test email sent to {message.email} (printed to console)'
        })
    except ContactMessage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Message not found'
        })