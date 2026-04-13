"""Storage backends for local development and Vercel Blob production uploads."""

import os

from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ImproperlyConfigured

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
        self.blob_token = os.getenv('VERCEL_BLOB_READ_WRITE_TOKEN') or os.getenv('BLOB_READ_WRITE_TOKEN')
        self.is_vercel = bool(os.getenv('VERCEL'))
    
    def _prepare_blob_path(self, name):
        """Normalize incoming pathnames for blob uploads."""
        return name.lstrip('/')

    def _is_url(self, name):
        return str(name).startswith('http://') or str(name).startswith('https://')
    
    def _save(self, name, content):
        """Save to Blob on Vercel and to filesystem locally."""
        if not self.is_vercel:
            return super()._save(name, content)

        if not self.blob_token:
            raise ImproperlyConfigured(
                'Missing Vercel Blob token. Set VERCEL_BLOB_READ_WRITE_TOKEN (or BLOB_READ_WRITE_TOKEN).'
            )

        file_content = content.read() if hasattr(content, 'read') else content
        blob_path = self._prepare_blob_path(name)

        # Always allow overwrite to avoid duplicate-path failures during profile updates.
        result = put(
            blob_path,
            file_content,
            {
                'token': self.blob_token,
                'allowOverwrite': True,
                'addRandomSuffix': True,
            },
            timeout=30,
            multipart=len(file_content) > 5 * 1024 * 1024,
        )

        # Store public blob URL in DB so templates can resolve immediately.
        return result.get('url', blob_path)
    
    def url(self, name):
        """Resolve URL for local path or already-uploaded blob URL."""
        if self._is_url(name):
            return name

        if not self.is_vercel:
            return super().url(name)

        if not self.blob_token:
            raise ImproperlyConfigured(
                'Missing Vercel Blob token. Set VERCEL_BLOB_READ_WRITE_TOKEN (or BLOB_READ_WRITE_TOKEN).'
            )

        try:
            metadata = head(name, {'token': self.blob_token}, timeout=10)
            return metadata.get('url', name)
        except Exception:
            return name
    
    def delete(self, name):
        """Delete file from Blob (Vercel) or filesystem (local)."""
        if not self.is_vercel:
            return super().delete(name)

        if not self.blob_token:
            return

        try:
            delete(name, {'token': self.blob_token}, timeout=10)
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
            return True

        try:
            head(name, {'token': self.blob_token}, timeout=5)
            return True
        except BlobRequestError:
            return False
        except Exception:
            return False
