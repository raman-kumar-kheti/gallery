import os
import threading
import numpy as np
import faiss
from typing import Optional
from pathlib import Path

from worker.config import settings


class FAISSService:
    """
    Manages per-event FAISS indexes.
    Each event has an isolated IndexFlatIP (inner product = cosine similarity for normalized vectors).

    Index file: {FAISS_INDEX_DIR}/event_{event_id}.index
    """

    _lock = threading.Lock()
    _loaded_indexes: dict[str, faiss.Index] = {}

    def _index_path(self, event_id: str) -> str:
        Path(settings.faiss_index_dir).mkdir(parents=True, exist_ok=True)
        return os.path.join(settings.faiss_index_dir, f"event_{event_id}.index")

    def _get_or_create_index(self, event_id: str, dimension: int = 512) -> faiss.Index:
        """Get an in-memory index or load from disk. Create new if not exists."""
        with self._lock:
            if event_id in self._loaded_indexes:
                return self._loaded_indexes[event_id]

            index_path = self._index_path(event_id)
            if os.path.exists(index_path):
                index = faiss.read_index(index_path)
            else:
                # IndexFlatIP: exact inner product search (cosine for normalized vectors)
                index = faiss.IndexFlatIP(dimension)

            self._loaded_indexes[event_id] = index
            return index

    def add_embedding(self, event_id: str, embedding: np.ndarray) -> int:
        """
        Add a face embedding to the event's FAISS index.
        Returns the FAISS position (faiss_pos) assigned to this vector.
        """
        index = self._get_or_create_index(event_id, dimension=embedding.shape[0])

        faiss_pos = index.ntotal  # Next position
        embedding_2d = embedding.reshape(1, -1).astype(np.float32)
        index.add(embedding_2d)

        # Persist to disk
        self._save_index(event_id, index)
        return faiss_pos

    def search(
        self,
        event_id: str,
        query_embedding: np.ndarray,
        top_k: int = 20,
        threshold: float = 0.5,
    ) -> list[int]:
        """
        Search for similar faces in the event's FAISS index.

        Returns a list of faiss_pos values for matched vectors.
        threshold: minimum inner product score (0.5 = ~60° angle for normalized vectors)
        """
        index = self._get_or_create_index(event_id)

        if index.ntotal == 0:
            return []

        query_2d = query_embedding.reshape(1, -1).astype(np.float32)
        scores, positions = index.search(query_2d, min(top_k, index.ntotal))

        # Filter by threshold and valid positions
        matched = []
        for score, pos in zip(scores[0], positions[0]):
            if pos >= 0 and score >= threshold:
                matched.append(int(pos))

        return matched

    def rebuild_index(self, event_id: str, embeddings: list[np.ndarray]) -> None:
        """
        Rebuild the entire FAISS index for an event from scratch.
        Used when photos are deleted or index is corrupted.
        """
        if not embeddings:
            return

        dimension = embeddings[0].shape[0]
        index = faiss.IndexFlatIP(dimension)

        matrix = np.vstack(embeddings).astype(np.float32)
        index.add(matrix)

        with self._lock:
            self._loaded_indexes[event_id] = index
            self._save_index(event_id, index)

    def _save_index(self, event_id: str, index: faiss.Index) -> None:
        """Persist FAISS index to disk."""
        index_path = self._index_path(event_id)
        faiss.write_index(index, index_path)

    def get_index_size(self, event_id: str) -> int:
        """Return number of vectors in the event's index."""
        index_path = self._index_path(event_id)
        if not os.path.exists(index_path):
            return 0
        index = faiss.read_index(index_path)
        return index.ntotal

    def delete_index(self, event_id: str) -> None:
        """Remove the FAISS index file for an event (when event is deleted)."""
        with self._lock:
            self._loaded_indexes.pop(event_id, None)
            index_path = self._index_path(event_id)
            if os.path.exists(index_path):
                os.remove(index_path)


faiss_service = FAISSService()
