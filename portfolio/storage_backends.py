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

            # Always prefer storing full URL so url() doesn't need extra lookups.
            # This makes image rendering faster and more reliable on Vercel.
            blob_url = result.get('url')
            if blob_url:
                # Blob URL is typically ~90-120 chars; Django FileField can hold 255+
                if len(blob_url) <= 200:
                    return blob_url
                # If URL is unexpectedly long, fall back to storing pathname
                return result.get('pathname', blob_path)

            # Fallback if put() didn't return a URL (shouldn't happen)
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
            if 'url' in metadata:
                return metadata['url']
            # If metadata exists but no url key, construct from pathname
            pathname = metadata.get('pathname', name)
            return self._construct_blob_url(pathname)
        except Exception:
            # If head() fails, construct URL as fallback
            # This ensures Vercel-hosted images always return a valid Blob URL
            return self._construct_blob_url(name)

    def _construct_blob_url(self, pathname):
        """Construct valid Vercel Blob URL from pathname."""
        # Public Vercel Blob store domain (works for all public blobs)
        pathname = pathname.lstrip('/')
        return f'https://blob.vercelusercontent.com/{pathname}'

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
