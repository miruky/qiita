"""
AWS SDK (Boto3) シリーズ #3
S3 バケットの作成・一覧・存在確認・削除
"""

import boto3
from botocore.exceptions import ClientError


def create_bucket():
    """バケットを作成する（東京リージョン）"""
    s3 = boto3.client('s3', region_name='ap-northeast-1')

    s3.create_bucket(
        Bucket='my-boto3-demo-20260308',
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-northeast-1'
        }
    )
    print("バケットを作成しました")


def list_buckets():
    """バケット一覧を取得する"""
    s3 = boto3.client('s3')

    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(f"{bucket['Name']}  作成日: {bucket['CreationDate']}")


def check_bucket_exists():
    """バケットの存在確認"""
    s3 = boto3.client('s3')

    try:
        s3.head_bucket(Bucket='my-boto3-demo-20260308')
        print("バケットは存在します")
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print("バケットは存在しません")
        elif error_code == 403:
            print("アクセス権限がありません")
        else:
            raise


def delete_bucket():
    """バケットを削除する"""
    s3 = boto3.client('s3')

    # 空のバケットを削除
    s3.delete_bucket(Bucket='my-boto3-demo-20260308')

    # 中身があるバケットを削除（Resource 版が便利）
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket('my-boto3-demo-20260308')
    bucket.objects.all().delete()   # 全オブジェクトを削除
    bucket.delete()                 # バケット本体を削除
    print("バケットを削除しました")
