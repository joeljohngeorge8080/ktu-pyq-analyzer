"""
Storage abstraction — swap local ↔ S3 by implementing StorageBackend.
"""
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from app.config import settings

class StorageBackend(ABC):
    @abstractmethod
    def save(self, src_path: str, dest_key: str) -> str:
        """Save file and return its accessible path/URL."""

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Return URL to serve the file."""

    @abstractmethod
    def delete(self, key: str):
        pass


class LocalStorage(StorageBackend):
    def __init__(self):
        self.base = settings.upload_path
        self.base.mkdir(parents=True, exist_ok=True)

    def save(self, src_path: str, dest_key: str) -> str:
        dest = self.base / dest_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest)
        return str(dest)

    def save_bytes(self, data: bytes, dest_key: str) -> str:
        dest = self.base / dest_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return str(dest)

    def get_url(self, key: str) -> str:
        return f"/static/{key}"

    def delete(self, key: str):
        path = self.base / key
        if path.exists():
            path.unlink()


# S3 stub – wire in boto3 when needed
class S3Storage(StorageBackend):
    def __init__(self, bucket: str, region: str):
        self.bucket = bucket
        self.region = region

    def save(self, src_path: str, dest_key: str) -> str:
        raise NotImplementedError("Configure boto3 and implement S3 upload here.")

    def get_url(self, key: str) -> str:
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

    def delete(self, key: str):
        raise NotImplementedError


# Active backend (swap to S3Storage for cloud)
storage = LocalStorage()
