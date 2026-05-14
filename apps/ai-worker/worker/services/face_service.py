import numpy as np
from typing import Optional
from insightface.app import FaceAnalysis

from worker.config import settings


class FaceService:
    """
    InsightFace wrapper for face detection and embedding generation.
    Singleton — loaded once per worker process.
    """

    _instance: Optional["FaceService"] = None
    _app: Optional[FaceAnalysis] = None

    def __new__(cls) -> "FaceService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self) -> None:
        if self._app is None:
            self._app = FaceAnalysis(
                name=settings.insightface_model,
                providers=["CPUExecutionProvider"],
            )
            self._app.prepare(ctx_id=-1, det_size=(640, 640))

    def get_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding from an image.
        Returns 512-dim float32 embedding vector, or None if no face detected.

        :param image: BGR numpy array (as returned by cv2.imread or PIL.Image converted)
        """
        self._load_model()
        faces = self._app.get(image)
        if not faces:
            return None
        # Use the largest face (most prominent)
        largest_face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        embedding = largest_face.embedding
        # Normalize to unit vector for cosine similarity
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.astype(np.float32)

    def get_all_embeddings(self, image: np.ndarray) -> list[np.ndarray]:
        """
        Extract embeddings for all detected faces in an image.
        Used for group photos where multiple faces may be present.
        """
        self._load_model()
        faces = self._app.get(image)
        embeddings = []
        for face in faces:
            emb = face.embedding.astype(np.float32)
            norm = np.linalg.norm(emb)
            if norm > 0:
                emb = emb / norm
            embeddings.append(emb)
        return embeddings

    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
        """Load image bytes into a numpy array for InsightFace."""
        import numpy as np
        from PIL import Image
        import io
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # InsightFace expects BGR
        img_array = np.array(pil_img)[:, :, ::-1]
        return img_array

    @staticmethod
    def load_image_from_url(url: str) -> np.ndarray:
        """Download image from URL and load into numpy array."""
        import urllib.request
        with urllib.request.urlopen(url) as response:
            image_bytes = response.read()
        return FaceService.load_image_from_bytes(image_bytes)


face_service = FaceService()
