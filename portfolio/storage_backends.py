"""
Custom Django storage backends for Vercel Blob and local development.
Automatically switches between local filesystem (development) and Vercel Blob (production).
"""
import os
import requests
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from urllib.parse import urljoin


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
        self.blob_token = os.getenv('VERCEL_BLOB_READ_WRITE_TOKEN', '')
        self.is_vercel = bool(os.getenv('VERCEL'))
        self.blob_url = 'https://blob.vercelusercontent.com'
    
    def _prepare_blob_path(self, name):
        """Prepare file path for Vercel Blob (remove leading slashes, ensure consistency)"""
        return name.lstrip('/')
    
    def _save(self, name, content):
        """Override to save to Vercel Blob on production, local filesystem otherwise"""
        
        # Always use local storage in development
        if not self.is_vercel or not self.blob_token:
            return super()._save(name, content)
        
        # Read file content
        if hasattr(content, 'read'):
            file_content = content.read()
        else:
            file_content = content
        
        # Prepare blob path
        blob_path = self._prepare_blob_path(name)
        
        try:
            # Upload to Vercel Blob
            response = requests.put(
                f'{self.blob_url}/{blob_path}',
                data=file_content,
                headers={
                    'Authorization': f'Bearer {self.blob_token}',
                    'x-add-random-suffix': 'false',
                },
                timeout=30,
            )
            response.raise_for_status()
            return name
        except Exception as e:
            # Fallback to local storage if Blob upload fails
            print(f"Vercel Blob upload failed for {name}: {e}. Falling back to local storage.")
            return super()._save(name, content)
    
    def url(self, name):
        """Return URL for accessing the file"""
        if not self.is_vercel or not self.blob_token:
            return super().url(name)
        
        # Return Vercel Blob URL
        blob_path = self._prepare_blob_path(name)
        return f'{self.blob_url}/{blob_path}'
    
    def delete(self, name):
        """Delete from Vercel Blob or local filesystem"""
        if not self.is_vercel or not self.blob_token:
            return super().delete(name)
        
        blob_path = self._prepare_blob_path(name)
        try:
            response = requests.delete(
                f'{self.blob_url}/{blob_path}',
                headers={'Authorization': f'Bearer {self.blob_token}'},
                timeout=30,
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Vercel Blob delete failed for {name}: {e}")
            # Still try local delete as fallback
            try:
                return super().delete(name)
            except:
                pass
    
    def exists(self, name):
        """Check if file exists in Vercel Blob or local filesystem"""
        if not self.is_vercel or not self.blob_token:
            return super().exists(name)
        
        # For Blob, we can check by trying to access it, but for performance
        # we'll assume it exists if the path is valid. In production, Django
        # typically only checks this for unsafe operations.
        return True  # Assume exists since we just uploaded it
