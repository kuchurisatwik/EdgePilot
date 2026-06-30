"""Storage backend seam. MVP = local filesystem; S3 can swap in later."""

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.core.config import settings

# Allowed image types -> file extension.
ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/webp": "webp",
}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class StorageError(Exception):
    pass


@dataclass(frozen=True)
class StoredFile:
    file_path: str  # relative to the storage root
    size_bytes: int
    content_type: str


class StorageBackend(Protocol):
    def save(
        self,
        user_id: uuid.UUID,
        trade_id: uuid.UUID,
        slot: str,
        *,
        content: bytes,
        content_type: str,
    ) -> StoredFile: ...

    def full_path(self, file_path: str) -> Path: ...

    def delete(self, file_path: str) -> None: ...


class LocalStorageBackend:
    def __init__(self, base_dir: str) -> None:
        self._base = Path(base_dir).resolve()

    def _resolve(self, file_path: str) -> Path:
        candidate = (self._base / file_path).resolve()
        # Path-traversal guard: must stay inside the storage root.
        if self._base not in candidate.parents and candidate != self._base:
            raise StorageError("Invalid storage path.")
        return candidate

    def save(
        self,
        user_id: uuid.UUID,
        trade_id: uuid.UUID,
        slot: str,
        *,
        content: bytes,
        content_type: str,
    ) -> StoredFile:
        ext = ALLOWED_CONTENT_TYPES[content_type]
        relative = f"{user_id}/{trade_id}/{slot}.{ext}"
        destination = self._resolve(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return StoredFile(file_path=relative, size_bytes=len(content), content_type=content_type)

    def full_path(self, file_path: str) -> Path:
        return self._resolve(file_path)

    def delete(self, file_path: str) -> None:
        path = self._resolve(file_path)
        if path.exists():
            path.unlink()


def get_storage_backend() -> StorageBackend:
    return LocalStorageBackend(settings.screenshot_dir)
