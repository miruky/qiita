"""
AWS SDK (Boto3) シリーズ #3
バケットポリシー・CORS・ライフサイクルルールの設定
"""

import json

import boto3


def set_bucket_policy():
    """バケットポリシーを設定する"""
    s3 = boto3.client('s3')

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::my-public-bucket/*"
            }
        ]
    }

    s3.put_bucket_policy(
        Bucket='my-public-bucket',
        Policy=json.dumps(policy)
    )


def get_bucket_policy():
    """バケットポリシーを取得する"""
    s3 = boto3.client('s3')

    response = s3.get_bucket_policy(Bucket='my-public-bucket')
    policy = json.loads(response['Policy'])
    print(json.dumps(policy, indent=2))


def set_cors():
    """CORS 設定"""
    s3 = boto3.client('s3')

    cors_config = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST'],
                'AllowedOrigins': ['https://example.com'],
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3000
            }
        ]
    }

    s3.put_bucket_cors(
        Bucket='my-bucket',
        CORSConfiguration=cors_config
    )


def set_lifecycle_rules():
    """ライフサイクルルールを設定する"""
    s3 = boto3.client('s3')

    lifecycle = {
        'Rules': [
            {
                'ID': 'MoveToGlacierAfter90Days',
                'Filter': {'Prefix': 'logs/'},
                'Status': 'Enabled',
                'Transitions': [
                    {
                        'Days': 90,
                        'StorageClass': 'GLACIER'
                    }
                ],
                'Expiration': {
                    'Days': 365  # 365 日後に削除
                }
            },
            {
                'ID': 'DeleteTempAfter7Days',
                'Filter': {'Prefix': 'temp/'},
                'Status': 'Enabled',
                'Expiration': {
                    'Days': 7
                }
            }
        ]
    }

    s3.put_bucket_lifecycle_configuration(
        Bucket='my-bucket',
        LifecycleConfiguration=lifecycle
    )
    print("ライフサイクルルールを設定しました")
