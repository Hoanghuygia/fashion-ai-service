from __future__ import annotations

from dataclasses import dataclass

import boto3
from botocore.config import Config

from app.config import get_settings


@dataclass(frozen=True)
class StorageClient:
    client: object
    bucket: str

    @classmethod
    def build(cls) -> "StorageClient":
        settings = get_settings()

        config = Config(
            s3={"addressing_style": "path" if settings.s3_path_style else "virtual"}
        )
        client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.s3_use_ssl,
            config=config,
        )

        return cls(client=client, bucket=settings.s3_bucket)

    def download(self, bucket: str, object_key: str) -> bytes:
        response = self.client.get_object(Bucket=bucket, Key=object_key)
        return response["Body"].read()

    def upload(self, bucket: str, object_key: str, data: bytes, content_type: str) -> None:
        self.client.put_object(
            Bucket=bucket,
            Key=object_key,
            Body=data,
            ContentType=content_type,
        )
