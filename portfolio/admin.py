from django.contrib import admin
from django.utils.html import format_html
from django.contrib import admin  # type: ignore
from django.contrib.auth.admin import UserAdmin  # type: ignore
from django.contrib.auth.models import User  # type: ignore
from django.utils.html import format_html  # type: ignore
from .models import *
from django.utils.safestring import mark_safe
from .models import ContactMessage
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import messages
from .services import send_email_with_admin_config, test_database_connection_from_admin, persist_active_database_runtime_config, get_runtime_database_status

# ==================== INLINE CLASSES ====================


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Portfolio Profile'
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'headline', 'summary')
        }),
        ('Profile Images', {
            'fields': ('profile_image', 'cover_image')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'location', 'website')
        }),
        ('Social Links', {
            'fields': ('linkedin', 'github', 'twitter', 'whatsapp', 'behance', 'instagram', 'facebook')
        }),
        ('Customization', {
            'fields': ('theme_color', 'accent_color', 'show_phone', 'show_email')
        }),
    )


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1
    fields = ('title', 'company', 'location', 'start_date', 'end_date',
              'currently_working', 'company_logo', 'company_url', 'description', 'order')
    ordering = ['-start_date']


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1
    fields = ('institution', 'degree', 'field_of_study', 'grade', 'start_date',
              'end_date', 'currently_studying', 'institution_logo',
              'institution_url', 'description', 'order')
    ordering = ['-start_date']


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ('name', 'category', 'level', 'proficiency', 'icon', 'order')
    ordering = ['category', 'order']


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1
    fields = ('title', 'description', 'technologies', 'project_url', 'github_url',
              'start_date', 'end_date', 'is_ongoing', 'thumbnail', 'featured', 'order')
    ordering = ['-start_date']


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 1
    fields = ('name', 'issuing_organization', 'issue_date', 'expiration_date',
              'credential_id', 'credential_url', 'order')
    ordering = ['-issue_date']


class MediaFileInline(admin.TabularInline):
    model = MediaFile
    fk_name = 'profile'
    extra = 1
    fields = ('project', 'file', 'title', 'description',
              'category', 'tags', 'allow_download', 'file_type')
    readonly_fields = ('file_type',)


class ProjectMediaInline(admin.TabularInline):
    model = MediaFile
    fk_name = 'project'
    extra = 1
    fields = ('file', 'title', 'description', 'category',
              'tags', 'allow_download', 'file_type')
    readonly_fields = ('file_type',)


class SectionVisibilityInline(admin.StackedInline):
    model = SectionVisibility
    can_delete = False
    verbose_name_plural = 'Section Visibility'
    fieldsets = (
        ('Section Toggles', {
            'fields': ('show_about', 'show_experience', 'show_education',
                       'show_skills', 'show_projects', 'show_certifications',
                       'show_media', 'show_contact')
        }),
        ('Layout Options', {
            'fields': ('layout_style',)
        }),
    )

# ========== DYNAMIC SECTIONS INLINES (MUST BE BEFORE ProfileAdmin) ==========


class DynamicSectionInline(admin.TabularInline):
    model = DynamicSection
    extra = 0
    fields = ('title', 'section_type', 'is_active',
              'order', 'show_title', 'layout_style')
    show_change_link = True
    classes = ['collapse']


class SectionItemInline(admin.TabularInline):
    model = SectionItem
    extra = 1
    fields = ('title', 'subtitle', 'image', 'icon', 'is_featured', 'order')
    classes = ['collapse']

# ==================== ADMIN CLASSES ====================


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'headline', 'email', 'location', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('first_name', 'last_name',
                     'email', 'headline', 'location')

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'first_name', 'last_name', 'headline', 'summary')
        }),
        ('Profile Images', {
            'fields': ('profile_image', 'cover_image'),
            'description': 'Upload profile and cover images'
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'location', 'website')
        }),
        ('Social Links', {
            'fields': ('linkedin', 'github', 'twitter', 'whatsapp', 'behance', 'instagram', 'facebook')
        }),
        ('Customization', {
            'fields': ('theme_color', 'accent_color', 'show_phone', 'show_email')
        }),
    )

    inlines = [
        SectionVisibilityInline,
        ExperienceInline,
        EducationInline,
        SkillInline,
        ProjectInline,
        CertificationInline,
        MediaFileInline,
        DynamicSectionInline,  # NOW THIS WILL WORK
    ]

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'  # type: ignore


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'category',
                    'project', 'allow_download', 'uploaded_at', 'file_preview')
    list_filter = ('file_type', 'category', 'project',
                   'allow_download', 'uploaded_at')
    search_fields = ('title', 'description', 'tags')
    readonly_fields = ('file_type', 'file_preview_display')

    fieldsets = (
        ('File Information', {
            'fields': ('profile', 'project', 'file', 'title', 'description')
        }),
        ('Categorization', {
            'fields': ('file_type', 'category', 'tags', 'allow_download')
        }),
        ('Preview', {
            'fields': ('file_preview_display',)
        }),
    )

    def file_preview(self, obj):
        """Preview for list view"""
        if obj.file and hasattr(obj.file, 'url'):
            if obj.file_type == 'image':
                return format_html('<img src="{}" height="50" style="border-radius: 5px;" />', obj.file.url)
            elif obj.file_type == 'pdf':
                return mark_safe('<span style="font-size: 24px; color: red;">📕</span>')
            elif obj.file_type == 'video':
                return mark_safe('<span style="font-size: 24px; color: blue;">🎬</span>')
            elif obj.file_type == 'audio':
                return mark_safe('<span style="font-size: 24px; color: green;">🎵</span>')
        return "-"
    file_preview.short_description = 'Preview'  # type: ignore

    def file_preview_display(self, obj):
        """Preview for detail/edit view"""
        if obj.file and hasattr(obj.file, 'url'):
            if obj.file_type == 'image':
                return format_html('<img src="{}" height="200" style="border-radius: 5px;" /><br><small>{}</small>',
                                   obj.file.url, obj.file.name)
            elif obj.file_type in ['pdf', 'document']:
                return format_html(
                    '<p><strong>Document File:</strong> <a href="{}" target="_blank">{}</a></p>'
                    '<p><span style="font-size: 48px; color: red;">📄</span></p>',
                    obj.file.url, obj.file.name
                )
            elif obj.file_type == 'video':
                return format_html(
                    '<p><strong>Video File:</strong> <a href="{}" target="_blank">{}</a></p>'
                    '<p><span style="font-size: 48px; color: blue;">🎥</span></p>',
                    obj.file.url, obj.file.name
                )
            elif obj.file_type == 'audio':
                return format_html(
                    '<p><strong>Audio File:</strong> <a href="{}" target="_blank">{}</a></p>'
                    '<p><span style="font-size: 48px; color: green;">🎵</span></p>',
                    obj.file.url, obj.file.name
                )
            else:
                return format_html(
                    '<p><strong>File:</strong> <a href="{}" target="_blank">{}</a></p>'
                    '<p><span style="font-size: 48px;">📁</span></p>',
                    obj.file.url, obj.file.name
                )
        return "No file uploaded"

    file_preview_display.short_description = 'File Preview'  # type: ignore


@admin.register(DynamicSection)
class DynamicSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'section_type',
                    'is_active', 'order', 'created_at')
    list_filter = ('section_type', 'is_active', 'layout_style')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'content')
    inlines = [SectionItemInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('profile', 'title', 'section_type', 'content')
        }),
        ('Display Settings', {
            'fields': ('show_title', 'icon', 'order', 'is_active', 'layout_style', 'css_class')
        }),
    )


@admin.register(SectionItem)
class SectionItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'is_featured', 'order')
    list_filter = ('is_featured', 'section__section_type')
    list_editable = ('order', 'is_featured')
    search_fields = ('title', 'subtitle', 'description')

    fieldsets = (
        ('Basic Information', {
            'fields': ('section', 'title', 'subtitle', 'description')
        }),
        ('Media', {
            'fields': ('image', 'icon')
        }),
        ('Additional Information', {
            'fields': ('date', 'date_text', 'url', 'url_text')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured')
        }),
    )

# ==================== USER ADMIN ====================


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'featured',
                    'is_ongoing', 'is_completed', 'allow_media_download', 'start_date', 'order')
    list_filter = ('featured', 'is_ongoing', 'is_completed',
                   'allow_media_download', 'start_date')
    search_fields = ('title', 'description', 'technologies')
    inlines = [ProjectMediaInline]
    fieldsets = (
        ('Project Information', {
            'fields': ('profile', 'title', 'description', 'technologies', 'thumbnail')
        }),
        ('Links', {
            'fields': ('project_url', 'github_url')
        }),
        ('Timeline and Visibility', {
            'fields': ('start_date', 'end_date', 'is_ongoing', 'is_completed', 'featured', 'allow_media_download', 'order')
        }),
    )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, MediaFile):
                if not instance.profile_id:
                    instance.profile_id = form.instance.profile_id
                if not instance.project_id:
                    instance.project_id = form.instance.id
            instance.save()

        for deleted_obj in formset.deleted_objects:
            deleted_obj.delete()

        formset.save_m2m()


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Certification)
admin.site.register(SectionVisibility)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read',
                    'is_responded', 'replied_at', 'reply_actions')
    list_filter = ('is_read', 'is_responded', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('submitted_at', 'updated_at', 'message_preview')
    list_editable = ('is_read', 'is_responded')
    actions = ('send_reply_email_action',)

    # Custom fieldsets for email reply
    fieldsets = (
        ('Original Message', {
            'fields': ('message_preview', 'name', 'email', 'subject', 'message')
        }),
        ('Reply to Sender', {
            'fields': ('reply_subject', 'reply_message')
        }),
        ('Status', {
            'fields': ('is_read', 'is_responded', 'replied_at')
        }),
        ('Metadata', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Custom method to display original message
    def message_preview(self, obj):
        return format_html('<div style="background:#f5f5f5;padding:10px;border-radius:5px;max-height:200px;overflow-y:auto;">'
                           '<strong>Original Message:</strong><br><br>'
                           '{}'
                           '</div>', obj.message)
    message_preview.short_description = 'Message Preview'

    # Action buttons in list view
    def reply_actions(self, obj):
        return format_html(
            '<div style="display:flex;gap:5px;">'
            '<a href="/admin/portfolio/contactmessage/{}/change/" class="button" style="padding:5px 10px;background:#007bff;color:white;border-radius:3px;text-decoration:none;">Reply</a>'
            '<button onclick="sendTestEmail({})" style="padding:5px 10px;background:#28a745;color:white;border-radius:3px;border:none;">Send</button>'
            '</div>',
            obj.id, obj.id
        )
    reply_actions.short_description = 'Actions'

    # Save method to send email when reply is added
    def save_model(self, request, obj, form, change):
        # If reply is provided, send email
        if obj.reply_message and not obj.is_responded:
            # Set default reply subject if not provided
            if not obj.reply_subject:
                obj.reply_subject = f"Re: {obj.subject}"

            # Send email (admin-managed SMTP or console fallback)
            try:
                send_email_with_admin_config(
                    obj.reply_subject,
                    obj.reply_message,
                    [obj.email],
                    fail_silently=False,
                )

                # Mark as responded
                obj.is_responded = True
                obj.replied_at = timezone.now()
                obj.sent_to_email = obj.email
                messages.success(request, f"Reply email sent to {obj.email}.")

            except Exception as e:
                messages.error(request, f"Error sending email: {e}")

        # Mark as read if not already
        if not obj.is_read:
            obj.is_read = True

        super().save_model(request, obj, form, change)

    # Add custom JavaScript to admin
    class Media:
        js = ('admin/js/contact_reply.js',)

    # Add notification count to admin
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        unread = ContactMessage.objects.filter(is_read=False).count()
        unresponded = ContactMessage.objects.filter(is_responded=False).count()

        extra_context.update({
            'unread_count': unread,
            'unresponded_count': unresponded,
            'title': f'Contact Messages ({unread} unread, {unresponded} pending)'
        })

        return super().changelist_view(request, extra_context=extra_context)

    def send_reply_email_action(self, request, queryset):
        sent_count = 0
        for message_obj in queryset:
            if message_obj.reply_message and not message_obj.is_responded:
                reply_subject = message_obj.reply_subject or f"Re: {message_obj.subject}"
                try:
                    send_email_with_admin_config(
                        reply_subject,
                        message_obj.reply_message,
                        [message_obj.email],
                        fail_silently=False,
                    )
                    message_obj.reply_subject = reply_subject
                    message_obj.is_responded = True
                    message_obj.replied_at = timezone.now()
                    message_obj.sent_to_email = message_obj.email
                    message_obj.save()
                    sent_count += 1
                except Exception:
                    continue

        if sent_count:
            self.message_user(
                request, f"Sent {sent_count} reply email(s).", level=messages.SUCCESS)
        else:
            self.message_user(
                request, "No emails were sent. Ensure selected messages have a reply message and are not already responded.", level=messages.WARNING)

    send_reply_email_action.short_description = 'Send reply email for selected messages'


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'email_backend',
                    'email_host_user', 'database_engine', 'runtime_database_badge', 'seo_site_name', 'updated_at')
    list_editable = ('is_active',)
    readonly_fields = ('runtime_database_badge',
                       'professional_setup_tips', 'updated_at',)
    actions = ('test_postgresql_connection', 'refresh_runtime_database_status')

    fieldsets = (
        ('General', {
            'fields': ('name', 'is_active', 'runtime_database_badge', 'professional_setup_tips', 'updated_at')
        }),
        ('Email Setup', {
            'fields': (
                'email_backend',
                'default_from_email',
                'admin_notification_email',
                'email_host',
                'email_port',
                'email_host_user',
                'email_host_password',
                'email_use_tls',
                'email_use_ssl',
            ),
            'description': 'Configure Gmail/SMTP credentials here (App Password supported).',
        }),
        ('Contact Auto-Reply', {
            'fields': (
                'auto_reply_enabled',
                'auto_reply_subject',
                'auto_reply_message',
            ),
            'description': 'Control and customize the confirmation email sent after a visitor submits the contact form.',
        }),
        ('PostgreSQL Database Setup', {
            'fields': (
                'database_engine',
                'database_name',
                'database_user',
                'database_password',
                'database_host',
                'database_port',
            ),
            'description': 'Store and validate PostgreSQL settings from admin. Use "Test PostgreSQL connection" action to verify.',
        }),
        ('SEO & Meta Setup', {
            'fields': (
                'seo_site_name',
                'seo_default_meta_title',
                'seo_default_meta_description',
                'seo_default_meta_keywords',
                'seo_meta_robots',
                'seo_canonical_base_url',
                'seo_og_image_url',
                'seo_twitter_card',
            ),
            'description': 'Tip: fill these once to power global SEO tags across your portfolio pages.',
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'email_host_password' in form.base_fields:
            form.base_fields['email_host_password'].widget.input_type = 'password'
            form.base_fields['email_host_password'].help_text = 'Use your Gmail App Password here.'
        if 'database_password' in form.base_fields:
            form.base_fields['database_password'].widget.input_type = 'password'
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.is_active:
            SystemConfiguration.objects.exclude(
                pk=obj.pk).update(is_active=False)

        runtime_config_path = persist_active_database_runtime_config()
        if runtime_config_path:
            self.message_user(
                request,
                f'Database runtime config updated at {runtime_config_path}. Restart the server to apply DB changes.',
                level=messages.INFO,
            )
        else:
            self.message_user(
                request,
                'Settings saved. Runtime DB file could not be persisted in this environment.',
                level=messages.WARNING,
            )

    def test_postgresql_connection(self, request, queryset):
        checked = 0
        for config in queryset:
            checked += 1
            success, message_text = test_database_connection_from_admin(config)
            if success:
                self.message_user(
                    request, f"{config.name}: {message_text}", level=messages.SUCCESS)
            else:
                self.message_user(
                    request, f"{config.name}: {message_text}", level=messages.ERROR)

        if checked == 0:
            self.message_user(
                request, 'No configuration selected.', level=messages.WARNING)

    test_postgresql_connection.short_description = 'Test PostgreSQL connection for selected configuration'

    def refresh_runtime_database_status(self, request, queryset):
        runtime_config_path = persist_active_database_runtime_config()
        status = get_runtime_database_status()
        self.message_user(
            request,
            f"Runtime DB status refreshed: {status.get('label', 'Unknown')} ({runtime_config_path or 'runtime file unavailable'})",
            level=messages.SUCCESS,
        )

    refresh_runtime_database_status.short_description = 'Refresh runtime DB status file'

    def runtime_database_badge(self, obj):
        status = get_runtime_database_status()
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;color:white;background:{};font-weight:600;">{}</span>',
            status.get('color', '#1f2937'),
            status.get('label', 'Unknown'),
        )

    runtime_database_badge.short_description = 'Current Active DB'  # type: ignore

    def professional_setup_tips(self, obj):
        return mark_safe(
            '<div style="padding:14px 16px;background:#f9fafb;border:1px solid #cbd5e1;border-radius:10px;line-height:1.65;color:#0f172a;font-size:14px;">'
            '<strong style="display:block;font-size:15px;margin-bottom:8px;color:#0b1220;">Professional Setup Tips</strong>'
            '<ul style="margin:0 0 0 20px;padding:0;">'
            '<li>Keep only one configuration active at a time.</li>'
            '<li>Use SQLite during local development and switch to PostgreSQL for production.</li>'
            '<li>After changing database settings, restart the server to apply updates.</li>'
            '<li>Use the action "Refresh runtime DB status file" to regenerate active runtime DB config.</li>'
            '<li>Fill SEO fields once so all pages get consistent professional metadata.</li>'
            '</ul>'
            '</div>'
        )

    professional_setup_tips.short_description = 'Configuration Guidance'  # type: ignore
