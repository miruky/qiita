"""
AWS SDK (Boto3) シリーズ #6
パフォーマンス最適化テクニック
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config


# ---------------------------------------------------------------------------
# 1. 接続プールのサイズ設定
# ---------------------------------------------------------------------------

def connection_pool():
    """接続プールサイズを拡大して並列リクエストに備える"""
    config = Config(
        max_pool_connections=50  # デフォルトは 10
    )
    s3 = boto3.client('s3', config=config)
    return s3


# ---------------------------------------------------------------------------
# 2. クライアントの使い回し
# ---------------------------------------------------------------------------

# NG：毎回クライアントを作成（接続の無駄）
def bad_get_object(bucket, key):
    s3 = boto3.client('s3')       # 毎回新しいクライアント
    return s3.get_object(Bucket=bucket, Key=key)


# OK：クライアントを使い回す
_s3_client = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client('s3')
    return _s3_client


def good_get_object(bucket, key):
    s3 = get_s3_client()
    return s3.get_object(Bucket=bucket, Key=key)


# ---------------------------------------------------------------------------
# 3. Lambda でのベストプラクティス
# ---------------------------------------------------------------------------

# Lambda 関数のトップレベルでクライアントを作成
# → コンテナ再利用時に接続を使い回せる
s3_for_lambda = boto3.client('s3')
dynamodb_for_lambda = boto3.resource('dynamodb')
table_for_lambda = dynamodb_for_lambda.Table('Products')


def lambda_handler(event, context):
    """ハンドラ内ではクライアントを再作成しない"""
    response = s3_for_lambda.get_object(
        Bucket=event['bucket'],
        Key=event['key']
    )
    return {'statusCode': 200}


# ---------------------------------------------------------------------------
# 4. Client はスレッドセーフ — ThreadPoolExecutor で並列処理
# ---------------------------------------------------------------------------

def parallel_download():
    """Client をスレッド間で共有して並列ダウンロードする"""
    s3 = boto3.client('s3')  # スレッド間で共有 OK

    def download_file(key):
        s3.download_file('my-bucket', key, f'/tmp/{key}')
        return key

    keys = [f'file_{i}.txt' for i in range(20)]

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_file, keys))

    print(f"{len(results)} ファイルをダウンロードしました")


def parallel_resource_safe():
    """Resource はスレッドセーフでないため各スレッドで作成する"""

    def process_item(item_key):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Products')
        response = table.get_item(Key=item_key)
        return response.get('Item')

    keys = [
        {'category': 'books', 'product_id': f'b{i:03d}'}
        for i in range(100)
    ]

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_item, keys))

    print(f"{len(results)} 件を取得しました")


# ---------------------------------------------------------------------------
# 5. asyncio + aioboto3（非公式ライブラリ）
# ---------------------------------------------------------------------------

async def async_list_buckets():
    """aioboto3 を使った非同期 S3 操作の例"""
    import aioboto3  # pip install aioboto3

    session = aioboto3.Session()
    async with session.client('s3') as s3:
        response = await s3.list_buckets()
        for bucket in response['Buckets']:
            print(bucket['Name'])


async def async_upload_files(files: list[str]):
    """aioboto3 で複数ファイルを非同期アップロードする"""
    import aioboto3

    session = aioboto3.Session()
    async with session.client('s3') as s3:
        tasks = [
            s3.upload_file(f, 'my-bucket', f'uploads/{f}')
            for f in files
        ]
        await asyncio.gather(*tasks)


# ---------------------------------------------------------------------------
# 6. S3 マルチパートアップロード設定
# ---------------------------------------------------------------------------

def optimized_upload():
    """TransferConfig でマルチパートアップロードを最適化する"""
    config = TransferConfig(
        multipart_threshold=8 * 1024 * 1024,   # 8 MB 以上でマルチパート
        max_concurrency=10,                     # 並列数
        multipart_chunksize=8 * 1024 * 1024,   # チャンクサイズ
        use_threads=True                        # スレッド使用
    )

    s3 = boto3.client('s3')
    s3.upload_file(
        'large_file.zip', 'my-bucket', 'large_file.zip',
        Config=config
    )


# ---------------------------------------------------------------------------
# 7. DynamoDB バッチ処理
# ---------------------------------------------------------------------------

def batch_write_1000():
    """batch_writer は自動で 25 件ずつ分割 + 未処理アイテムの自動リトライ"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    items = [
        {
            'category': f'cat{i}',
            'product_id': f'p{i:04d}',
            'price': Decimal(str(i * 100)),
        }
        for i in range(1000)
    ]

    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    print("1000 件を書き込みました")


# ---------------------------------------------------------------------------
# 8. Paginator で大量データを効率的に処理
# ---------------------------------------------------------------------------

def efficient_pagination():
    """ページごとに処理して全件をメモリに載せない"""
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    total = 0
    for page in paginator.paginate(Bucket='my-bucket', Prefix='logs/'):
        contents = page.get('Contents', [])
        total += len(contents)
        for obj in contents:
            pass  # ページごとに処理
    print(f"合計: {total} オブジェクト")


# ---------------------------------------------------------------------------
# 9. 必要な属性のみ取得（ProjectionExpression）
# ---------------------------------------------------------------------------

def projection_expression():
    """不要な属性を転送しないことで転送量を削減する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    # OK：必要な属性だけを取得
    response = table.scan(
        ProjectionExpression='#n',
        ExpressionAttributeNames={'#n': 'name'}
    )
    names = [item['name'] for item in response['Items']]
    print(f"{len(names)} 件の name を取得")


# ---------------------------------------------------------------------------
# 10. ロギングとデバッグ
# ---------------------------------------------------------------------------

def enable_debug_logging():
    """Boto3 / botocore のデバッグログを有効化する"""
    boto3.set_stream_logger('boto3', logging.DEBUG)
    boto3.set_stream_logger('botocore', logging.DEBUG)

    s3 = boto3.client('s3')
    s3.list_buckets()  # リクエスト/レスポンスの詳細がログに出力される


def selective_logging():
    """特定カテゴリのみログを出力する"""
    # botocore の HTTP リクエストのみ
    logging.getLogger('botocore.httpsession').setLevel(logging.DEBUG)

    # 認証情報の解決プロセス
    logging.getLogger('botocore.credentials').setLevel(logging.DEBUG)

    # リトライ状況
    logging.getLogger('botocore.retries').setLevel(logging.DEBUG)

    logging.basicConfig(level=logging.DEBUG)
