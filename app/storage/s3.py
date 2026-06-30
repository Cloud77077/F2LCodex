import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
import boto3
from app.storage.base import Storage

class S3Storage(Storage):
    def __init__(self, bucket: str, endpoint_url: str | None, region: str, access_key: str | None, secret_key: str | None):
        self.bucket = bucket
        self.client = boto3.client("s3", endpoint_url=endpoint_url, region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    async def save(self, source: Path, key: str) -> None:
        await asyncio.to_thread(self.client.upload_file, str(source), self.bucket, key)
    async def open(self, key: str, start: int = 0, end: int | None = None) -> AsyncIterator[bytes]:
        kwargs = {"Bucket": self.bucket, "Key": key}
        if start or end is not None:
            kwargs["Range"] = f"bytes={start}-{'' if end is None else end}"
        obj = await asyncio.to_thread(self.client.get_object, **kwargs)
        body = obj["Body"]
        while True:
            chunk = await asyncio.to_thread(body.read, 1024 * 1024)
            if not chunk: break
            yield chunk
    async def delete(self, key: str) -> None:
        await asyncio.to_thread(self.client.delete_object, Bucket=self.bucket, Key=key)
    def local_path(self, key: str) -> Path | None:
        return None
