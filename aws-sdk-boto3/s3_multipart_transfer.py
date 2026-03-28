"""
AWS SDK (Boto3) シリーズ #3
マルチパートアップロードと TransferConfig
"""

import boto3
from boto3.s3.transfer import TransferConfig


def upload_with_transfer_config():
    """TransferConfig で大容量ファイルをアップロードする"""
    s3 = boto3.client('s3')

    config = TransferConfig(
        multipart_threshold=8 * 1024 * 1024,   # 8MB 以上でマルチパート
        max_concurrency=10,                     # 同時転送数
        multipart_chunksize=8 * 1024 * 1024,   # パートサイズ 8MB
        use_threads=True                        # マルチスレッド使用
    )

    s3.upload_file(
        'large_video.mp4',
        'my-bucket',
        'videos/large_video.mp4',
        Config=config
    )


def manual_multipart_upload():
    """手動マルチパートアップロード"""
    s3 = boto3.client('s3')
    bucket = 'my-bucket'
    key = 'videos/huge_file.mp4'
    file_path = 'huge_file.mp4'
    part_size = 100 * 1024 * 1024  # 100MB

    # マルチパートアップロードを開始
    upload = s3.create_multipart_upload(Bucket=bucket, Key=key)
    upload_id = upload['UploadId']

    parts = []
    part_number = 1

    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(part_size)
                if not data:
                    break

                response = s3.upload_part(
                    Bucket=bucket,
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=data
                )

                parts.append({
                    'PartNumber': part_number,
                    'ETag': response['ETag']
                })
                print(f"Part {part_number} uploaded")
                part_number += 1

        # 完了
        s3.complete_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        print("マルチパートアップロード完了")

    except Exception as e:
        # エラー時はアップロードを中止
        s3.abort_multipart_upload(
            Bucket=bucket, Key=key, UploadId=upload_id
        )
        raise e
