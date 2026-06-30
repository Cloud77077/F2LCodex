import os, shutil, aiofiles
from collections.abc import AsyncIterator
from pathlib import Path
from app.storage.base import Storage

class LocalStorage(Storage):
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
    def _path(self, key: str) -> Path:
        safe = key.replace("..", "").lstrip("/")
        return self.root / safe
    async def save(self, source: Path, key: str) -> None:
        dest = self._path(key); dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    async def open(self, key: str, start: int = 0, end: int | None = None) -> AsyncIterator[bytes]:
        remaining = None if end is None else end - start + 1
        async with aiofiles.open(self._path(key), "rb") as f:
            await f.seek(start)
            while remaining is None or remaining > 0:
                chunk = await f.read(1024 * 1024 if remaining is None else min(1024 * 1024, remaining))
                if not chunk: break
                if remaining is not None: remaining -= len(chunk)
                yield chunk
    async def delete(self, key: str) -> None:
        try: os.remove(self._path(key))
        except FileNotFoundError: pass
    def local_path(self, key: str) -> Path | None:
        return self._path(key)
