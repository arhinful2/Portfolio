import os
import logging

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_core.settings')

logger = logging.getLogger(__name__)


def _is_vercel_runtime():
    return bool(
        os.getenv('VERCEL')
        or os.getenv('VERCEL_ENV')
        or os.getenv('NOW_REGION')
    )


def _ensure_migrations_applied():
    if not _is_vercel_runtime():
        return

    if os.getenv('SKIP_STARTUP_MIGRATIONS'):
        return

    try:
        call_command('migrate', interactive=False, verbosity=0)
    except Exception as exc:
        logger.exception('Startup migration check failed: %s', exc)
        raise


_ensure_migrations_applied()

app = get_wsgi_application()
handler = app
