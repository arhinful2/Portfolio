from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0004_contactmessage_replied_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    default='Default Configuration', max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('email_backend', models.CharField(choices=[
                 ('smtp', 'SMTP (Gmail/Custom SMTP)'), ('console', 'Console (development)')], default='smtp', max_length=20)),
                ('default_from_email', models.EmailField(
                    blank=True, max_length=254, null=True)),
                ('admin_notification_email', models.EmailField(
                    blank=True, max_length=254, null=True)),
                ('email_host', models.CharField(blank=True,
                 default='smtp.gmail.com', max_length=255, null=True)),
                ('email_port', models.PositiveIntegerField(default=587)),
                ('email_host_user', models.CharField(
                    blank=True, max_length=255, null=True)),
                ('email_host_password', models.CharField(
                    blank=True, max_length=255, null=True)),
                ('email_use_tls', models.BooleanField(default=True)),
                ('email_use_ssl', models.BooleanField(default=False)),
                ('database_engine', models.CharField(choices=[
                 ('sqlite', 'SQLite'), ('postgresql', 'PostgreSQL')], default='sqlite', max_length=20)),
                ('database_name', models.CharField(
                    blank=True, max_length=255, null=True)),
                ('database_user', models.CharField(
                    blank=True, max_length=255, null=True)),
                ('database_password', models.CharField(
                    blank=True, max_length=255, null=True)),
                ('database_host', models.CharField(
                    blank=True, max_length=255, null=True)),
                ('database_port', models.CharField(blank=True,
                 default='5432', max_length=20, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'System Configuration',
                'verbose_name_plural': 'System Configuration',
            },
        ),
    ]
