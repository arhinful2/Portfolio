from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.db.utils import load_backend
from pathlib import Path
import json

from .models import SystemConfiguration


def get_system_configuration():
    config = SystemConfiguration.get_active()
    if config:
        return config
    return None


def send_email_with_admin_config(subject, message, recipients, fail_silently=False):
    config = get_system_configuration()

    if config and config.email_backend == 'smtp':
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=config.email_host or 'smtp.gmail.com',
            port=config.email_port or 587,
            username=config.email_host_user,
            password=config.email_host_password,
            use_tls=config.email_use_tls,
            use_ssl=config.email_use_ssl,
            fail_silently=fail_silently,
        )
        from_email = config.default_from_email or config.email_host_user or settings.DEFAULT_FROM_EMAIL
    else:
        connection = get_connection(
            backend='django.core.mail.backends.console.EmailBackend')
        from_email = settings.DEFAULT_FROM_EMAIL

    return send_mail(
        subject,
        message,
        from_email,
        recipients,
        connection=connection,
        fail_silently=fail_silently,
    )


def notify_admin_for_contact_message(contact_message):
    config = get_system_configuration()
    if not config or not config.admin_notification_email:
        return False

    subject = f"New Contact Message: {contact_message.subject}"
    body = (
        f"You received a new contact message.\n\n"
        f"Name: {contact_message.name}\n"
        f"Email: {contact_message.email}\n"
        f"Subject: {contact_message.subject}\n\n"
        f"Message:\n{contact_message.message}"
    )

    send_email_with_admin_config(
        subject, body, [config.admin_notification_email], fail_silently=False)
    return True


def build_database_config_from_admin(config):
    if not config or config.database_engine != 'postgresql':
        return None

    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config.database_name,
        'USER': config.database_user,
        'PASSWORD': config.database_password,
        'HOST': config.database_host,
        'PORT': config.database_port or '5432',
    }


def test_database_connection_from_admin(config):
    db_config = build_database_config_from_admin(config)
    if not db_config:
        return False, 'Database engine is not set to PostgreSQL.'

    required_values = ['NAME', 'USER', 'PASSWORD', 'HOST']
    missing = [key for key in required_values if not db_config.get(key)]
    if missing:
        return False, f"Missing required database fields: {', '.join(missing)}"

    try:
        backend = load_backend(db_config['ENGINE'])
        connection = backend.DatabaseWrapper(
            db_config, alias='admin_test_connection')
        connection.ensure_connection()
        connection.close()
        return True, 'PostgreSQL connection successful.'
    except Exception as exc:
        return False, f"PostgreSQL connection failed: {exc}"


def _database_runtime_config_path():
    runtime_dir = Path(settings.BASE_DIR) / '.runtime'
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / 'database_runtime_config.json'


def persist_active_database_runtime_config():
    config = SystemConfiguration.get_active()
    db_config = build_database_config_from_admin(config)

    runtime_payload = {'database_engine': 'sqlite'}

    if config and config.database_engine == 'postgresql' and db_config:
        required_values = ['NAME', 'USER', 'PASSWORD', 'HOST']
        missing = [key for key in required_values if not db_config.get(key)]
        if not missing:
            runtime_payload = {
                'database_engine': 'postgresql',
                'database_name': db_config.get('NAME'),
                'database_user': db_config.get('USER'),
                'database_password': db_config.get('PASSWORD'),
                'database_host': db_config.get('HOST'),
                'database_port': db_config.get('PORT') or '5432',
            }

    path = _database_runtime_config_path()
    with path.open('w', encoding='utf-8') as handle:
        json.dump(runtime_payload, handle, indent=2)

    return path


def get_runtime_database_status():
    path = _database_runtime_config_path()

    if not path.exists():
        return {
            'engine': 'sqlite',
            'label': 'SQLite (default)',
            'color': '#2563eb',
        }

    try:
        with path.open('r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except Exception:
        return {
            'engine': 'unknown',
            'label': 'Unknown (invalid runtime config)',
            'color': '#b91c1c',
        }

    engine = payload.get('database_engine')
    if engine == 'postgresql':
        host = payload.get('database_host') or 'unknown-host'
        name = payload.get('database_name') or 'unknown-db'
        return {
            'engine': 'postgresql',
            'label': f'PostgreSQL ({name} @ {host})',
            'color': '#15803d',
        }

    return {
        'engine': 'sqlite',
        'label': 'SQLite (default)',
        'color': '#2563eb',
    }
