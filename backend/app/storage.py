import asyncio
import uuid

import boto3
from botocore.config import Config

from app.config import (
    R2_ACCOUNT_ID,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    R2_PUBLIC_URL,
)


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def build_object_key(album_slug: str, original_filename: str) -> str:
    """Унікальний ключ файлу в бакеті, згрупований по папці альбому."""
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[-1].lower()
    return f"albums/{album_slug}/{uuid.uuid4().hex}{ext}"


def build_public_url(key: str) -> str:
    base = R2_PUBLIC_URL.rstrip("/")
    return f"{base}/{key}"


def _upload_fileobj_sync(fileobj, key: str, content_type: str | None) -> None:
    client = get_r2_client()
    extra_args = {"ContentType": content_type} if content_type else {}
    client.upload_fileobj(fileobj, R2_BUCKET_NAME, key, ExtraArgs=extra_args)


def _delete_object_sync(key: str) -> None:
    client = get_r2_client()
    client.delete_object(Bucket=R2_BUCKET_NAME, Key=key)


async def upload_fileobj(fileobj, key: str, content_type: str | None = None) -> str:
    """
    Завантажує файл у R2 і повертає публічний URL.
    boto3 не має async-клієнта, тому виконуємо блокуючий виклик
    в окремому потоці (asyncio.to_thread), щоб не блокувати event loop.
    """
    await asyncio.to_thread(_upload_fileobj_sync, fileobj, key, content_type)
    return build_public_url(key)


async def delete_object(key: str) -> None:
    await asyncio.to_thread(_delete_object_sync, key)
