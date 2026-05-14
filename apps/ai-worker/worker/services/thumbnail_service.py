import io
from PIL import Image


class ThumbnailService:
    """Generate thumbnails from images using Pillow."""

    DEFAULT_SIZE = (400, 400)
    QUALITY = 85

    def generate_thumbnail(
        self,
        image_bytes: bytes,
        max_size: tuple[int, int] = DEFAULT_SIZE,
    ) -> bytes:
        """
        Generate a JPEG thumbnail from image bytes.
        Maintains aspect ratio. Returns JPEG bytes.
        """
        img = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB (handles PNG with transparency, CMYK, etc.)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Thumbnail maintains aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=self.QUALITY, optimize=True)
        output.seek(0)
        return output.read()

    def get_dimensions(self, image_bytes: bytes) -> tuple[int, int]:
        """Return (width, height) of image."""
        img = Image.open(io.BytesIO(image_bytes))
        return img.size


thumbnail_service = ThumbnailService()
