"""
AWS SDK (Boto3) シリーズ #2
Session・Client・Resource の使い分け
"""

import boto3


# =============================================================
# Session：設定と認証の管理
# =============================================================

def session_basics():
    """Session の基本操作"""
    # デフォルト Session を使ったクライアント作成
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    # プロファイルとリージョンを指定して Session を作成
    session = boto3.Session(
        profile_name='dev',
        region_name='us-west-2'
    )
    s3 = session.client('s3')
    ec2 = session.resource('ec2')
    return s3, ec2


def multi_region_sessions():
    """複数リージョンの Session を使い分ける"""
    tokyo_session = boto3.Session(
        profile_name='default',
        region_name='ap-northeast-1'
    )
    virginia_session = boto3.Session(
        profile_name='default',
        region_name='us-east-1'
    )

    tokyo_s3 = tokyo_session.client('s3')
    virginia_s3 = virginia_session.client('s3')

    tokyo_buckets = tokyo_s3.list_buckets()
    virginia_buckets = virginia_s3.list_buckets()
    return tokyo_buckets, virginia_buckets


def session_info():
    """Session が保持する情報を確認する"""
    session = boto3.Session()

    print(session.get_available_services())
    print(session.get_available_regions('s3'))
    print(session.region_name)
    print(session.profile_name)


# =============================================================
# Client：低レベルインターフェース
# =============================================================

def client_basics():
    """Client の基本操作"""
    s3 = boto3.client('s3')

    # バケット一覧取得 → 辞書が返る
    response = s3.list_buckets()
    print(type(response))  # <class 'dict'>
    print(response['Buckets'][0]['Name'])
    print(response['ResponseMetadata']['HTTPStatusCode'])


def client_s3_operations():
    """Client で S3 を操作する"""
    s3 = boto3.client('s3')

    # バケット作成
    s3.create_bucket(
        Bucket='my-new-bucket-20260308',
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-northeast-1'
        }
    )

    # オブジェクトアップロード
    s3.put_object(
        Bucket='my-new-bucket-20260308',
        Key='hello.txt',
        Body=b'Hello, Boto3!'
    )

    # オブジェクト取得
    response = s3.get_object(
        Bucket='my-new-bucket-20260308',
        Key='hello.txt'
    )
    content = response['Body'].read().decode('utf-8')
    print(content)  # Hello, Boto3!


def create_service_clients():
    """各サービスの Client 作成例"""
    s3 = boto3.client('s3')
    ec2 = boto3.client('ec2')
    dynamodb = boto3.client('dynamodb')
    lambda_client = boto3.client('lambda')  # lambda は予約語なので注意
    sqs = boto3.client('sqs')
    sns = boto3.client('sns')
    sts = boto3.client('sts')
    iam = boto3.client('iam')
    return s3, ec2, dynamodb, lambda_client, sqs, sns, sts, iam


# =============================================================
# Resource：高レベルインターフェース
# =============================================================

def resource_basics():
    """Resource の基本操作"""
    s3 = boto3.resource('s3')

    # バケット一覧をオブジェクトとして取得
    for bucket in s3.buckets.all():
        print(bucket.name)
        print(bucket.creation_date)


def resource_s3_operations():
    """Resource で S3 を操作する"""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('my-bucket')

    # ファイルアップロード
    bucket.upload_file('local_file.txt', 'remote_file.txt')

    # オブジェクト一覧
    for obj in bucket.objects.all():
        print(f"{obj.key}  ({obj.size} bytes)")

    # オブジェクト操作
    obj = s3.Object('my-bucket', 'hello.txt')
    obj.put(Body=b'Hello from Resource!')
    print(obj.content_length)
    print(obj.last_modified)

    # ファイルダウンロード
    obj.download_file('downloaded.txt')


# =============================================================
# Client と Resource の比較
# =============================================================

def compare_client_vs_resource():
    """同じ操作を Client と Resource で比較する"""
    # === Client 版 ===
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket='my-bucket')
    for obj in response.get('Contents', []):
        print(f"{obj['Key']}  ({obj['Size']} bytes)")

    # ページネーション（1000 件以上ある場合）
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket='my-bucket'):
        for obj in page.get('Contents', []):
            print(f"{obj['Key']}  ({obj['Size']} bytes)")

    # === Resource 版 ===
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket('my-bucket')
    for obj in bucket.objects.all():  # ページネーション自動
        print(f"{obj.key}  ({obj.size} bytes)")


# =============================================================
# 型ヒントと boto3-stubs
# =============================================================

def typed_s3_example():
    """
    型ヒント付きの S3 操作例
    事前準備: pip install 'boto3-stubs[essential]'
    """
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import ListObjectsV2OutputTypeDef

    def list_s3_objects(bucket_name: str) -> ListObjectsV2OutputTypeDef:
        s3: S3Client = boto3.client('s3')
        return s3.list_objects_v2(Bucket=bucket_name)

    result = list_s3_objects('my-bucket')
    for obj in result.get('Contents', []):
        print(obj['Key'])
