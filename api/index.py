import os
import logging

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_core.settings')

app = get_wsgi_application()

logger = logging.getLogger(__name__)


def _is_vercel_runtime():
    return bool(
        os.getenv('VERCEL')
        or os.getenv('VERCEL_ENV')
        or os.getenv('NOW_REGION')
    )


def _ensure_portfolio_schema():
    """Best-effort schema sync for production runtime.

    This runs after Django app setup to avoid AppRegistry startup errors.
    It only targets the portfolio app migration path and never raises,
    so the function won't crash if migration cannot run in this invocation.
    """
    if not _is_vercel_runtime():
        return

    try:
        call_command('migrate', 'portfolio', interactive=False, verbosity=0)
    except Exception as exc:
        logger.warning('Runtime portfolio migration check skipped: %s', exc)


_ensure_portfolio_schema()

handler = app
