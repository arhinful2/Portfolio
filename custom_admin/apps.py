from django.apps import AppConfig

class CustomAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_admin'
    verbose_name = 'Custom Admin'
    
    def ready(self):
        # Import signals when app is ready
        import custom_admin.signals
        # Patch the admin
        import custom_admin.admin