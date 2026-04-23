"""Storage backends for local development and Vercel Blob production uploads."""

import os
import posixpath
import uuid
from urllib.parse import urlparse

from django.core.files.storage import FileSystemStorage

from vercel_blob import put, head, delete
from vercel_blob.errors import BlobRequestError


class VercelBlobStorage(FileSystemStorage):
    """
    Hybrid storage backend:
    - On Vercel: uploads to Vercel Blob via REST API
    - Locally: stores to filesystem (default Django behavior)

    Environment variables required on Vercel:
    - VERCEL_BLOB_READ_WRITE_TOKEN: Get from Vercel dashboard > Storage > Blob > Tokens
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blob_token = os.getenv(
            'VERCEL_BLOB_READ_WRITE_TOKEN') or os.getenv('BLOB_READ_WRITE_TOKEN')
        self.is_vercel = bool(os.getenv('VERCEL'))

    def _prepare_blob_path(self, name):
        """Normalize and shorten incoming pathnames for blob uploads."""
        normalized = name.replace('\\', '/').lstrip('/')
        folder, filename = posixpath.split(normalized)

        # Keep path short and URL-safe so FileField max_length (100) is not exceeded
        # when saving full blob URLs.
        _, ext = os.path.splitext(filename)
        needs_short_name = (
            len(normalized) > 40
            or ' ' in filename
            or any(ch in filename for ch in ['(', ')', '[', ']', '#', '?', '&'])
        )

        if needs_short_name:
            short_name = f"{uuid.uuid4().hex[:18]}{ext.lower()}"
            normalized = posixpath.join(
                folder, short_name) if folder else short_name

        return normalized

    def _is_url(self, name):
        return str(name).startswith('http://') or str(name).startswith('https://')

    def _extract_pathname(self, name):
        """Return a normalized blob pathname for URL or plain path input."""
        value = str(name or '').strip()
        if not value:
            return ''

        if self._is_url(value):
            parsed = urlparse(value)
            return parsed.path.lstrip('/')

        return value.lstrip('/')

    def _save(self, name, content):
        """Save to Blob on Vercel and to filesystem locally."""
        if not self.is_vercel:
            return super()._save(name, content)

        file_content = content.read() if hasattr(content, 'read') else content
        blob_path = self._prepare_blob_path(name)

        if not self.blob_token:
            # Safety fallback: if token is missing in production, avoid hard 500.
            return super()._save(blob_path, content)

        try:
            # Use deterministic short path to avoid DB length overflow issues.
            result = put(
                blob_path,
                file_content,
                {
                    'token': self.blob_token,
                    'allowOverwrite': True,
                    'addRandomSuffix': False,
                },
                timeout=30,
                multipart=len(file_content) > 5 * 1024 * 1024,
            )

            # Persist only pathname to avoid FileField max_length truncation issues.
            # URL is resolved dynamically in url().
            saved_pathname = self._extract_pathname(result.get('pathname', blob_path))
            return saved_pathname or blob_path
        except Exception:
            # Keep admin save resilient even if blob request fails.
            return super()._save(blob_path, content)

    def url(self, name):
        """Resolve URL for local path or already-uploaded blob URL."""
        if not name:
            return ''

        pathname = self._extract_pathname(name)

        if self._is_url(name):
            # For legacy URL values, re-resolve canonical URL from pathname if possible.
            if not self.is_vercel or not self.blob_token:
                return name

            try:
                metadata = head(pathname, {'token': self.blob_token}, timeout=10)
                return metadata.get('url', name)
            except Exception:
                return name

        if not self.is_vercel:
            return super().url(name)

        if not self.blob_token:
            return super().url(name)

        try:
            metadata = head(pathname, {'token': self.blob_token}, timeout=10)
            return metadata.get('url', name)
        except Exception:
            # Keep graceful fallback for templates even if metadata lookup fails.
            return name

    def delete(self, name):
        """Delete file from Blob (Vercel) or filesystem (local)."""
        if not self.is_vercel:
            return super().delete(name)

        if not self.blob_token:
            return

        try:
            pathname = self._extract_pathname(name)
            if pathname:
                delete(pathname, {'token': self.blob_token}, timeout=10)
        except Exception:
            # Ignore delete failures to avoid breaking admin update/delete actions.
            return

    def exists(self, name):
        """Check existence for name resolution and collision handling."""
        if not self.is_vercel:
            return super().exists(name)

        if not self.blob_token:
            return False

        if self._is_url(name):
            name = self._extract_pathname(name)

        try:
            head(name, {'token': self.blob_token}, timeout=5)
            return True
        except BlobRequestError:
            return False
        except Exception:
            return False
