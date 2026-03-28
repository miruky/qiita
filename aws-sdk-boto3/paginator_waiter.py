"""
AWS SDK (Boto3) シリーズ #2
Paginator（ページネーション）と Waiter（状態待ち）
"""

import boto3


# =============================================================
# Paginator：大量データの取得
# =============================================================

def paginator_basic():
    """Paginator の基本的な使い方"""
    s3 = boto3.client('s3')

    paginator = s3.get_paginator('list_objects_v2')

    total = 0
    for page in paginator.paginate(Bucket='my-bucket'):
        for obj in page.get('Contents', []):
            total += 1
            print(f"{obj['Key']}")

    print(f"合計: {total} オブジェクト")


def paginator_with_config():
    """ページサイズと最大件数を指定する"""
    s3 = boto3.client('s3')

    paginator = s3.get_paginator('list_objects_v2')

    page_iterator = paginator.paginate(
        Bucket='my-bucket',
        PaginationConfig={
            'PageSize': 100,    # 1 回の API 呼び出しで取得する件数
            'MaxItems': 500     # 合計の最大件数
        }
    )

    for page in page_iterator:
        for obj in page.get('Contents', []):
            print(obj['Key'])


def paginator_with_jmespath():
    """JMESPath フィルタと組み合わせる"""
    s3 = boto3.client('s3')

    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket='my-bucket')

    # .jpg ファイルの Key だけをフラットに取得
    filtered = page_iterator.search("Contents[?ends_with(Key, '.jpg')].Key")
    for key in filtered:
        print(key)


# =============================================================
# Waiter：リソースの状態待ち
# =============================================================

def waiter_ec2_example():
    """EC2 インスタンスが running になるまで待機"""
    ec2 = boto3.client('ec2')

    ec2.start_instances(InstanceIds=['i-1234567890abcdef0'])

    waiter = ec2.get_waiter('instance_running')
    waiter.wait(
        InstanceIds=['i-1234567890abcdef0'],
        WaiterConfig={
            'Delay': 15,       # ポーリング間隔（秒）
            'MaxAttempts': 40   # 最大試行回数
        }
    )
    print("インスタンスが起動しました")


def waiter_s3_example():
    """S3 バケットが作成されるまで待機"""
    s3 = boto3.client('s3')

    s3.create_bucket(
        Bucket='my-new-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-1'}
    )

    waiter = s3.get_waiter('bucket_exists')
    waiter.wait(Bucket='my-new-bucket')
    print("バケットが作成されました")
