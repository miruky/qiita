"""
AWS SDK (Boto3) シリーズ #3
署名付き URL（Presigned URL）の生成
"""

import boto3


def generate_download_url():
    """ダウンロード用の署名付き URL を生成する"""
    s3 = boto3.client('s3', region_name='ap-northeast-1')

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': 'my-bucket',
            'Key': 'reports/confidential.pdf'
        },
        ExpiresIn=3600  # 60 分間有効（秒）
    )

    print(f"ダウンロードURL: {url}")
    return url


def generate_upload_url():
    """アップロード用の署名付き URL を生成する"""
    s3 = boto3.client('s3', region_name='ap-northeast-1')

    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': 'my-bucket',
            'Key': 'uploads/user_upload.jpg',
            'ContentType': 'image/jpeg'
        },
        ExpiresIn=600  # 10 分
    )

    print(f"アップロードURL: {url}")
    return url


def generate_presigned_post():
    """署名付き POST（フォームアップロード）を生成する"""
    s3 = boto3.client('s3', region_name='ap-northeast-1')

    response = s3.generate_presigned_post(
        Bucket='my-bucket',
        Key='uploads/${filename}',
        Fields={'Content-Type': 'image/jpeg'},
        Conditions=[
            {'Content-Type': 'image/jpeg'},
            ['content-length-range', 1, 10485760]  # 1B〜10MB
        ],
        ExpiresIn=600
    )

    print(f"URL: {response['url']}")
    print(f"Fields: {response['fields']}")
    return response
