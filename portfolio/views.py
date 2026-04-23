from .models import ContactMessage
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Profile, MediaFile, Project, DynamicSection, ContactMessage
from .services import notify_admin_for_contact_message, send_email_with_admin_config, send_contact_auto_reply


# Update the get_portfolio_data function (add this parameter)
def get_portfolio_data(profile, request=None):
    """Helper function to get all portfolio data with dynamic sections"""
    data = {
        'profile': profile,
        'visibility': profile.visibility if hasattr(profile, 'visibility') else None,
    }

    # Only get data for sections that are visible
    if hasattr(profile, 'visibility') and profile.visibility:
        visibility = profile.visibility

        if visibility.show_experience:
            data['experiences'] = profile.experiences.all()

        if visibility.show_education:
            data['educations'] = profile.educations.all()

        if visibility.show_skills:
            # Group skills by category
            skills_by_category = {}
            for skill in profile.skills.all():
                category = skill.category or 'Other'
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill)
            data['skills_by_category'] = skills_by_category

        if visibility.show_projects:
            data['projects'] = profile.projects.all()
            data['featured_projects'] = profile.projects.filter(featured=True)

        if visibility.show_certifications:
            data['certifications'] = profile.certifications.all()

        if visibility.show_media:
            data['media_files'] = profile.media_files.all()[:12]

    # ALWAYS GET DYNAMIC SECTIONS (they manage their own visibility)
    data['dynamic_sections'] = profile.dynamic_sections.filter(
        is_active=True).order_by('order')

    return data

# Update PortfolioHomeView to handle POST requests


class PortfolioHomeView(TemplateView):
    """Main portfolio view"""
    template_name = 'portfolio/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Handle contact form submission"""
        if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Handle AJAX request
            return self.handle_ajax_contact(request)

        # Handle regular form submission
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_content = request.POST.get('message', '').strip()

        if name and email and subject and message_content:
            # Save to database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_content
            )

            try:
                notify_admin_for_contact_message(contact_message)
            except Exception as exc:
                print(f"Admin notification email failed: {exc}")

            try:
                send_contact_auto_reply(contact_message)
            except Exception as exc:
                print(f"Contact auto-reply email failed: {exc}")

            # Print to terminal (for testing)
            print("\n" + "="*50)
            print("NEW CONTACT MESSAGE RECEIVED:")
            print("="*50)
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Subject: {subject}")
            print(f"Message: {message_content}")
            print(f"Time: {timezone.now()}")
            print("="*50 + "\n")

            # Add success message
            messages.success(
                request, 'Your message has been sent successfully!')

            # If it's an AJAX request, return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Message sent successfully!'
                })
        else:
            messages.error(request, 'Please fill in all required fields.')

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please fill in all required fields.'
                })

        # Redirect back to home page
        return redirect('portfolio_home')

    def handle_ajax_contact(self, request):
        """Handle AJAX contact form submission"""
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_content = request.POST.get('message', '').strip()

        if name and email and subject and message_content:
            # Save to database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_content
            )

            try:
                notify_admin_for_contact_message(contact_message)
            except Exception as exc:
                print(f"Admin notification email failed: {exc}")

            try:
                send_contact_auto_reply(contact_message)
            except Exception as exc:
                print(f"Contact auto-reply email failed: {exc}")

            # Print to terminal
            print("\n" + "="*50)
            print("NEW CONTACT MESSAGE RECEIVED (AJAX):")
            print("="*50)
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Subject: {subject}")
            print(f"Message: {message_content}")
            print(f"Time: {timezone.now()}")
            print("="*50 + "\n")

            return JsonResponse({
                'success': True,
                'message': 'Message sent successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.'
            })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.first()

        if profile:
            portfolio_data = get_portfolio_data(profile, self.request)
            # Rename keys to match template
            portfolio_data['portfolio_profile'] = portfolio_data.pop(
                'profile', None)
            portfolio_data['portfolio_visibility'] = portfolio_data.pop(
                'visibility', None)
            context.update(portfolio_data)

        return context


class MediaGalleryView(ListView):
    """Media gallery view"""
    model = MediaFile
    template_name = 'portfolio/media_gallery.html'
    context_object_name = 'media_files'
    paginate_by = 20

    def get_queryset(self):
        profile = Profile.objects.first()
        if profile:
            return MediaFile.objects.filter(profile=profile)
        return MediaFile.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.first()
        context['profile'] = profile

        # Group media by type for filter
        media_by_type = {}
        for media in context['media_files']:
            if media.file_type not in media_by_type:
                media_by_type[media.file_type] = []
            media_by_type[media.file_type].append(media)
        context['media_by_type'] = media_by_type

        return context


class ProjectDetailView(DetailView):
    """Project detail view"""
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.first()
        return context


def contact_view(request):
    """Contact form view"""
    profile = Profile.objects.first()
    return render(request, 'portfolio/contact.html', {'profile': profile})


def contact_ajax_view(request):
    """AJAX endpoint for contact form"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_content = request.POST.get('message', '').strip()

        if name and email and subject and message_content:
            # Save to database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_content
            )

            try:
                notify_admin_for_contact_message(contact_message)
            except Exception as exc:
                print(f"Admin notification email failed: {exc}")

            try:
                send_contact_auto_reply(contact_message)
            except Exception as exc:
                print(f"Contact auto-reply email failed: {exc}")

            # Print to terminal
            print("\n" + "="*50)
            print("NEW CONTACT MESSAGE RECEIVED (AJAX Endpoint):")
            print("="*50)
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Subject: {subject}")
            print(f"Message: {message_content}")
            print(f"Time: {timezone.now()}")
            print("="*50 + "\n")

            return JsonResponse({
                'success': True,
                'message': 'Message sent successfully!'
            })

        return JsonResponse({
            'success': False,
            'message': 'Please fill in all required fields.'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def send_test_email(request, message_id):
    """Send test email for a message using admin-managed configuration"""
    if request.method == 'GET' and request.user.is_staff:
        try:
            message = ContactMessage.objects.get(id=message_id)

            send_email_with_admin_config(
                f"Re: {message.subject}",
                "[Test reply from admin]",
                [message.email],
                fail_silently=False,
            )

            # Update message status
            message.is_read = True
            message.is_responded = True
            message.replied_at = timezone.now()
            message.save()

            return JsonResponse({
                'success': True,
                'message': f'Test email sent to {message.email}'
            })
        except ContactMessage.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Message not found'
            })

    return JsonResponse({
        'success': False,
        'message': 'Unauthorized'
    })


def debug_contact(request):
    """Debug endpoint to test contact form"""
    if request.method == 'POST':
        import json
        print("\n" + "="*60)
        print("DEBUG ENDPOINT - FORM DATA:")
        print("="*60)
        print(json.dumps(dict(request.POST), indent=2))
        print("="*60 + "\n")

        import sys
        sys.stdout.flush()

        return JsonResponse({
            'success': True,
            'message': 'Printed to console!',
            'data': dict(request.POST)
        })
    return JsonResponse({'error': 'POST only'})

# In your PortfolioHomeView post method, update the print statements:


def post(self, request, *args, **kwargs):
    """Handle contact form submission"""
    print("\n" + "="*60)
    print("POST REQUEST RECEIVED - CONTACT FORM")
    print("="*60)
    print(f"Request Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"POST Data: {dict(request.POST)}")
    print("="*60)

    # Your existing code, but add this at the beginning:
    import sys
    sys.stdout.flush()  # Force print to show immediately
