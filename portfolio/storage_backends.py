"""Storage backends for local development and Vercel Blob production uploads."""

import os
import posixpath
import uuid

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
        self.blob_token = os.getenv('VERCEL_BLOB_READ_WRITE_TOKEN') or os.getenv('BLOB_READ_WRITE_TOKEN')
        self.is_vercel = bool(os.getenv('VERCEL'))
    
    def _prepare_blob_path(self, name):
        """Normalize and shorten incoming pathnames for blob uploads."""
        normalized = name.replace('\\', '/').lstrip('/')
        folder, filename = posixpath.split(normalized)

        # Keep DB-stored file names within Django FileField default length limits.
        # Example output: user_1/profile/3f9a6f3f8a4f4c88a8cb4bc6baf6c53c.jpg
        if len(normalized) > 95:
            _, ext = os.path.splitext(filename)
            filename = f"{uuid.uuid4().hex}{ext.lower()}"
            normalized = posixpath.join(folder, filename) if folder else filename

        return normalized

    def _is_url(self, name):
        return str(name).startswith('http://') or str(name).startswith('https://')
    
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

            # Store blob pathname in DB (not full URL) so FileField length is safe.
            return result.get('pathname', blob_path)
        except Exception:
            # Keep admin save resilient even if blob request fails.
            return super()._save(blob_path, content)
    
    def url(self, name):
        """Resolve URL for local path or already-uploaded blob URL."""
        if self._is_url(name):
            return name

        if not self.is_vercel:
            return super().url(name)

        if not self.blob_token:
            return super().url(name)

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
