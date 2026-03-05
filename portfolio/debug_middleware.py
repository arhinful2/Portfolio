import sys

class PrintPostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Print POST data for contact form
        if request.method == 'POST' and 'name' in request.POST:
            print("\n" + "="*60)
            print("DEBUG: FORM SUBMISSION DETECTED")
            print("="*60)
            print(f"Name: {request.POST.get('name')}")
            print(f"Email: {request.POST.get('email')}")
            print(f"Subject: {request.POST.get('subject')}")
            print(f"Message: {request.POST.get('message')}")
            print("="*60 + "\n")
            sys.stdout.flush()
        
        response = self.get_response(request)
        return response