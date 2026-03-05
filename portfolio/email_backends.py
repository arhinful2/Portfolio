import sys
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend

class PrintEmailBackend(ConsoleEmailBackend):
    """Custom email backend that always prints to console"""
    def write_message(self, message):
        # Force print to stdout
        msg = message.message()
        print("\n" + "="*60)
        print("EMAIL WOULD BE SENT:")
        print("="*60)
        print(f"To: {message.to}")
        print(f"Subject: {message.subject}")
        print(f"Body:\n{message.body}")
        print("="*60 + "\n")
        
        # Flush immediately
        sys.stdout.flush()