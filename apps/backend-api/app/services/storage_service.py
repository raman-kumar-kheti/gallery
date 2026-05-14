import boto3
from botocore.config import Config
from typing import BinaryIO
import uuid

from app.config import settings


class StorageService:
    """Cloudflare R2 (S3-compatible) storage service."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = boto3.client(
                "s3",
                endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
        return self._client

    def upload_file(
        self,
        file_obj: BinaryIO,
        key: str,
        content_type: str = "image/jpeg",
    ) -> str:
        """
        Upload a file to R2 and return the public URL.
        Key example: events/{event_id}/images/{image_id}.jpg
        """
        self.client.upload_fileobj(
            file_obj,
            settings.r2_bucket_name,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        return f"{settings.r2_public_url}/{key}"

    def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: str = "image/jpeg",
    ) -> str:
        """Upload raw bytes to R2 and return public URL."""
        import io
        return self.upload_file(io.BytesIO(data), key, content_type)

    def generate_presigned_upload_url(
        self,
        key: str,
        content_type: str = "image/jpeg",
        expires_in: int = 3600,
    ) -> dict:
        """
        Generate a presigned URL for direct client-side uploads.
        Returns: {url, fields} for use with multipart form POST.
        """
        response = self.client.generate_presigned_post(
            settings.r2_bucket_name,
            key,
            Fields={"Content-Type": content_type},
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 1, 50 * 1024 * 1024],  # 50 MB max
            ],
            ExpiresIn=expires_in,
        )
        return response

    def delete_file(self, key: str) -> None:
        self.client.delete_object(Bucket=settings.r2_bucket_name, Key=key)

    @staticmethod
    def make_image_key(event_id: uuid.UUID, image_id: uuid.UUID, ext: str = "jpg") -> str:
        return f"events/{event_id}/images/{image_id}.{ext}"

    @staticmethod
    def make_thumbnail_key(event_id: uuid.UUID, image_id: uuid.UUID) -> str:
        return f"events/{event_id}/thumbnails/{image_id}_thumb.jpg"

    @staticmethod
    def make_selfie_key(event_id: uuid.UUID, session_id: uuid.UUID) -> str:
        return f"events/{event_id}/selfies/{session_id}.jpg"


storage_service = StorageService()
