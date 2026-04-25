from django.db import models  # type: ignore
from django.contrib.auth.models import User  # type: ignore
from tinymce.models import HTMLField  # type: ignore
import os
import html
from django.utils import timezone
from django.utils.html import strip_tags


def user_directory_path(instance, filename):
    """File will be uploaded to MEDIA_ROOT/user_<id>/<filename>"""
    user = None

    # For Profile instances
    if hasattr(instance, 'user') and instance.user:
        user = instance.user

    # For models with profile ForeignKey (Experience, Education, Skill, etc.)
    elif hasattr(instance, 'profile') and instance.profile:
        user = instance.profile.user

    # For SectionItem instances (which go through section -> profile -> user)
    elif hasattr(instance, 'section') and instance.section:
        if hasattr(instance.section, 'profile') and instance.section.profile:
            user = instance.section.profile.user

    if user:
        # Create a folder structure based on model type
        model_name = instance.__class__.__name__.lower()
        return f'user_{user.id}/{model_name}/{filename}'

    return f'uploads/{filename}'


class Profile(models.Model):
    """Main profile model - LinkedIn style"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)

    # Basic Information
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    headline = models.CharField(max_length=200, blank=True, null=True)
    summary = HTMLField(blank=True, null=True)

    # Profile Images (LinkedIn style)
    cover_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True,
                                    help_text="Recommended size: 1500x500px")
    profile_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True,
                                      help_text="Recommended size: 400x400px")

    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Social Links
    linkedin = models.URLField(
        blank=True, null=True, verbose_name="LinkedIn URL")
    github = models.URLField(blank=True, null=True, verbose_name="GitHub URL")
    twitter = models.URLField(blank=True, null=True)
    whatsapp = models.URLField(
        blank=True, null=True, verbose_name="WhatsApp URL")
    behance = models.URLField(blank=True, null=True,
                              verbose_name="Behance URL")
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)

    # Customization
    theme_color = models.CharField(
        max_length=7, default='#0073b1', help_text="Main theme color (hex)")
    accent_color = models.CharField(max_length=7, default='#333333', blank=True, null=True,
                                    help_text="Accent color (hex)")

    # Visibility Settings
    show_phone = models.BooleanField(
        default=False, verbose_name="Show phone publicly")
    show_email = models.BooleanField(
        default=False, verbose_name="Show email publicly")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Portfolio Profile"
        verbose_name_plural = "Portfolio Profiles"

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or "Profile"

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


class Experience(models.Model):
    """Work Experience"""
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=200, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)

    description = HTMLField(blank=True, null=True)
    order = models.IntegerField(default=0)

    # Optional fields
    company_logo = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    company_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date', 'order']
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experiences"

    def __str__(self):
        return f"{self.title or 'Position'} at {self.company or 'Company'}"


class Education(models.Model):
    """Education History"""
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200, blank=True, null=True)
    degree = models.CharField(max_length=200, blank=True, null=True)
    field_of_study = models.CharField(max_length=200, blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    currently_studying = models.BooleanField(default=False)

    description = HTMLField(blank=True, null=True)
    order = models.IntegerField(default=0)

    # Optional fields
    institution_logo = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    institution_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date', 'order']
        verbose_name = "Education"
        verbose_name_plural = "Educations"

    def __str__(self):
        return f"{self.degree or 'Degree'} at {self.institution or 'Institution'}"


class Skill(models.Model):
    """Skills with categories"""
    SKILL_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(
        max_length=20, choices=SKILL_LEVELS, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True,
                                help_text="e.g., Programming, Design, Tools")

    # Optional
    icon = models.CharField(max_length=100, blank=True, null=True,
                            help_text="Font Awesome icon class (e.g., fab fa-python)")
    proficiency = models.IntegerField(default=0, blank=True, null=True,
                                      help_text="Percentage (0-100)")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return self.name or "Skill"


class Project(models.Model):
    """Portfolio Projects"""
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200, blank=True, null=True)
    description = HTMLField(blank=True, null=True)

    # Project details
    technologies = models.CharField(max_length=500, blank=True, null=True,
                                    help_text="Comma-separated list")
    project_url = models.URLField(
        blank=True, null=True, verbose_name="Live Demo URL")
    github_url = models.URLField(
        blank=True, null=True, verbose_name="GitHub Repository URL")

    # Dates
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=False)
    is_completed = models.BooleanField(
        default=False,
        help_text="Mark this project as completed"
    )

    # Media
    thumbnail = models.ImageField(upload_to=user_directory_path, blank=True, null=True,
                                  help_text="Project thumbnail image")

    # Flags
    featured = models.BooleanField(
        default=False, help_text="Feature this project prominently")
    allow_media_download = models.BooleanField(
        default=True,
        help_text="Allow visitors to download this project's media files"
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['-start_date', 'order']
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title or "Project"

    def get_technologies_list(self):
        """Return technologies as list"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',')]
        return []

    @property
    def status_label(self):
        if self.is_completed:
            return 'Completed'
        if self.is_ongoing:
            return 'Ongoing'
        return 'In Progress'


class Certification(models.Model):
    """Professional Certifications"""
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200, blank=True, null=True)
    issuing_organization = models.CharField(
        max_length=200, blank=True, null=True)

    issue_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True,
                                       help_text="Leave blank if never expires")

    credential_id = models.CharField(max_length=100, blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True,
                                     help_text="URL to verify credential")

    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['-issue_date', 'order']
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"

    def __str__(self):
        return self.name or "Certification"


class MediaFile(models.Model):
    """Multi-type media files (images, videos, audio, documents, PSD, etc.)"""
    FILE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('pdf', 'PDF'),
        ('psd', 'PSD File'),
        ('ai', 'AI File'),
        ('figma', 'Figma File'),
        ('sketch', 'Sketch File'),
        ('other', 'Other'),
    ]

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='media_files')
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, related_name='media_files', blank=True, null=True,
        help_text="Optional: attach this media to a specific project")
    file = models.FileField(upload_to=user_directory_path)
    file_type = models.CharField(
        max_length=20, choices=FILE_TYPES, blank=True, null=True)

    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Optional categorization
    category = models.CharField(max_length=100, blank=True, null=True,
                                help_text="e.g., Logos, Mockups, Wireframes")
    tags = models.CharField(max_length=300, blank=True, null=True,
                            help_text="Comma-separated tags")
    allow_download = models.BooleanField(
        default=True,
        help_text="Allow this specific media file to be downloaded"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Media File"
        verbose_name_plural = "Media Files"

    def __str__(self):
        return self.title or self.file.name

    def save(self, *args, **kwargs):
        """Auto-detect file type from extension"""
        if self.project_id and not self.profile_id:
            self.profile_id = self.project.profile_id

        if self.description:
            # Media descriptions should remain plain text in cards/list views.
            cleaned = strip_tags(self.description)
            self.description = html.unescape(cleaned).strip()

        if not self.file_type:
            ext = os.path.splitext(self.file.name)[1].lower()

            # Image files
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']:
                self.file_type = 'image'

            # Video files
            elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                self.file_type = 'video'

            # Audio files
            elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                self.file_type = 'audio'

            # PDF files
            elif ext == '.pdf':
                self.file_type = 'pdf'

            # Document files
            elif ext in ['.doc', '.docx', '.txt', '.rtf', '.odt']:
                self.file_type = 'document'

            # Design files
            elif ext == '.psd':
                self.file_type = 'psd'
            elif ext == '.ai':
                self.file_type = 'ai'
            elif ext == '.fig':
                self.file_type = 'figma'
            elif ext == '.sketch':
                self.file_type = 'sketch'

            # Other
            else:
                self.file_type = 'other'

        super().save(*args, **kwargs)

    @property
    def file_extension(self):
        return os.path.splitext(self.file.name)[1][1:].upper()


class SectionVisibility(models.Model):
    """Control which sections are visible on the portfolio"""
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name='visibility')

    # Section toggles
    show_about = models.BooleanField(
        default=True, verbose_name="About Section")
    show_experience = models.BooleanField(
        default=True, verbose_name="Experience Section")
    show_education = models.BooleanField(
        default=True, verbose_name="Education Section")
    show_skills = models.BooleanField(
        default=True, verbose_name="Skills Section")
    show_projects = models.BooleanField(
        default=True, verbose_name="Projects Section")
    show_certifications = models.BooleanField(
        default=True, verbose_name="Certifications Section")
    show_media = models.BooleanField(
        default=True, verbose_name="Media Gallery Section")
    show_contact = models.BooleanField(
        default=True, verbose_name="Contact Section")

    # Navbar ordering controls (smaller number appears first)
    nav_about_order = models.PositiveIntegerField(
        default=10,
        help_text="Navbar position for About link"
    )
    nav_experience_order = models.PositiveIntegerField(
        default=20,
        help_text="Navbar position for Experience link"
    )
    nav_education_order = models.PositiveIntegerField(
        default=30,
        help_text="Navbar position for Education link"
    )
    nav_projects_order = models.PositiveIntegerField(
        default=40,
        help_text="Navbar position for Projects link"
    )
    nav_skills_order = models.PositiveIntegerField(
        default=50,
        help_text="Navbar position for Skills link"
    )
    nav_media_order = models.PositiveIntegerField(
        default=60,
        help_text="Navbar position for Media link"
    )
    nav_contact_order = models.PositiveIntegerField(
        default=70,
        help_text="Navbar position for Contact link"
    )

    # Layout options
    layout_style = models.CharField(max_length=20, default='linkedin',
                                    choices=[
                                        ('linkedin', 'LinkedIn Style'),
                                        ('minimal', 'Minimal'),
                                        ('creative', 'Creative'),
                                        ('corporate', 'Corporate'),
                                    ])

    class Meta:
        verbose_name = "Section Visibility"
        verbose_name_plural = "Section Visibility Settings"

    def __str__(self):
        return f"Visibility settings for {self.profile}"


class DynamicSection(models.Model):
    """Fully dynamic sections that clients can add/edit/delete"""
    SECTION_TYPES = [
        ('custom', 'Custom Section'),
        ('text', 'Text Content'),
        ('gallery', 'Image Gallery'),
        ('testimonials', 'Testimonials'),
        ('services', 'Services'),
        ('awards', 'Awards & Honors'),
        ('publications', 'Publications'),
        ('languages', 'Languages'),
        ('hobbies', 'Hobbies & Interests'),
        ('volunteer', 'Volunteer Work'),
    ]

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='dynamic_sections')
    title = models.CharField(max_length=200, blank=True, null=True)
    section_type = models.CharField(
        max_length=50, choices=SECTION_TYPES, default='custom')
    content = HTMLField(blank=True, null=True,
                        help_text="Main content for the section")

    # Display settings
    show_title = models.BooleanField(
        default=True, help_text="Show section title")
    icon = models.CharField(max_length=100, blank=True, null=True,
                            help_text="Font Awesome icon (e.g., fas fa-award)")
    order = models.IntegerField(
        default=0, help_text="Display order (lower = first)")
    is_active = models.BooleanField(
        default=True, help_text="Show this section")

    # Layout options
    layout_style = models.CharField(max_length=50, default='default',
                                    choices=[
                                        ('default', 'Default'),
                                        ('card', 'Card Style'),
                                        ('minimal', 'Minimal'),
                                        ('highlight', 'Highlight'),
                                    ])

    # Custom CSS class for advanced styling
    css_class = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Dynamic Section"
        verbose_name_plural = "Dynamic Sections"

    def __str__(self):
        return f"{self.title} ({self.section_type})"


class SectionItem(models.Model):
    """Individual items within a dynamic section (for galleries, lists, etc.)"""
    section = models.ForeignKey(
        'DynamicSection', on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200, blank=True, null=True)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Media
    image = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)

    # Dates/Additional info
    date = models.DateField(blank=True, null=True)
    date_text = models.CharField(max_length=100, blank=True, null=True)

    # Links
    url = models.URLField(blank=True, null=True)
    url_text = models.CharField(max_length=100, blank=True, null=True)

    # Ordering
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', '-is_featured', 'title']
        verbose_name = "Section Item"
        verbose_name_plural = "Section Items"

    def __str__(self):
        return self.title or f"Item {self.id}"  # type: ignore


# Add this after the existing models in models.py
class ContactMessage(models.Model):
    """Model to store contact form submissions"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    # Status fields
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)

    # Email reply fields
    reply_subject = models.CharField(max_length=200, blank=True, null=True)
    reply_message = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    sent_to_email = models.EmailField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.subject} - {self.name}"

    # Admin notes
    admin_notes = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.subject} - {self.name}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def mark_as_responded(self, notes=None):
        self.is_responded = True
        self.admin_notes = notes
        self.responded_at = timezone.now()
        self.save()


class SystemConfiguration(models.Model):
    """Admin-manageable app configuration (email + database)"""

    EMAIL_BACKEND_CHOICES = [
        ('smtp', 'SMTP (Gmail/Custom SMTP)'),
        ('console', 'Console (development)'),
    ]

    DATABASE_ENGINE_CHOICES = [
        ('sqlite', 'SQLite'),
        ('postgresql', 'PostgreSQL'),
    ]

    name = models.CharField(
        max_length=100, default='Default Configuration', unique=True)
    is_active = models.BooleanField(default=True)

    email_backend = models.CharField(
        max_length=20, choices=EMAIL_BACKEND_CHOICES, default='smtp')
    default_from_email = models.EmailField(blank=True, null=True)
    admin_notification_email = models.EmailField(blank=True, null=True)
    email_host = models.CharField(
        max_length=255, blank=True, null=True, default='smtp.gmail.com')
    email_port = models.PositiveIntegerField(default=587)
    email_host_user = models.CharField(max_length=255, blank=True, null=True)
    email_host_password = models.CharField(
        max_length=255, blank=True, null=True)
    email_use_tls = models.BooleanField(default=True)
    email_use_ssl = models.BooleanField(default=False)

    auto_reply_enabled = models.BooleanField(
        default=True,
        help_text="Automatically send a confirmation email to people who submit the contact form.")
    auto_reply_subject = models.CharField(
        max_length=255,
        default='Thanks for contacting {site_name}',
        help_text="Placeholders supported: {name}, {subject}, {site_name}")
    auto_reply_message = models.TextField(
        default=(
            'Hello {name},\n\n'
            'Thank you for contacting me through my portfolio website. '
            'I have received your message and will get back to you as soon as possible.\n\n'
            'Your message summary:\n'
            'Subject: {subject}\n'
            'Message: {message}\n\n'
            'Best regards,\n'
            '{site_name}\n'
            '{support_email}'
        ),
        help_text="Placeholders supported: {name}, {email}, {subject}, {message}, {site_name}, {support_email}")

    database_engine = models.CharField(
        max_length=20, choices=DATABASE_ENGINE_CHOICES, default='sqlite')
    database_name = models.CharField(max_length=255, blank=True, null=True)
    database_user = models.CharField(max_length=255, blank=True, null=True)
    database_password = models.CharField(max_length=255, blank=True, null=True)
    database_host = models.CharField(max_length=255, blank=True, null=True)
    database_port = models.CharField(
        max_length=20, blank=True, null=True, default='5432')

    seo_site_name = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Tip: your brand/site name (e.g., John Doe Portfolio)."
    )
    seo_default_meta_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Tip: keep title around 50-60 characters for search results."
    )
    seo_default_meta_description = models.TextField(
        blank=True,
        null=True,
        help_text="Tip: write a clear summary in about 150-160 characters."
    )
    seo_default_meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Tip: comma-separated words (optional for modern SEO)."
    )
    seo_og_image_url = models.URLField(
        blank=True,
        null=True,
        help_text="Tip: full image URL used for social sharing (Open Graph/Twitter)."
    )
    favicon_image = models.ImageField(
        upload_to='site_assets/',
        blank=True,
        null=True,
        help_text="Upload a favicon image for the site header/browser tab. Recommended: square PNG or JPG."
    )
    seo_twitter_card = models.CharField(
        max_length=30,
        choices=[
            ('summary', 'summary'),
            ('summary_large_image', 'summary_large_image'),
        ],
        default='summary_large_image',
        help_text="Tip: use summary_large_image for better social previews."
    )
    seo_meta_robots = models.CharField(
        max_length=80,
        default='index,follow',
        help_text="Tip: common values are index,follow or noindex,nofollow."
    )
    seo_canonical_base_url = models.URLField(
        blank=True,
        null=True,
        help_text="Tip: set your main domain, e.g., https://example.com"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"

    def __str__(self):
        return self.name

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).order_by('-updated_at').first()
