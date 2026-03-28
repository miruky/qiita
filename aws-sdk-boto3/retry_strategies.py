"""
AWS SDK (Boto3) シリーズ #6
リトライ戦略・タイムアウト設定
"""

import random
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


# ---------------------------------------------------------------------------
# 1. Config でリトライモードを設定
# ---------------------------------------------------------------------------

def standard_retry():
    """standard モード（推奨）— 指数バックオフ + ジッター"""
    config = Config(
        retries={
            'mode': 'standard',
            'max_attempts': 5   # 最大試行回数（リトライ回数ではない）
        }
    )
    s3 = boto3.client('s3', config=config)
    return s3


def adaptive_retry():
    """adaptive モード — トークンバケット方式（実験的）

    NOTE: adaptive モードは動作が変更される可能性があるため、
    本番環境では standard モードが推奨です。
    """
    config = Config(
        retries={
            'mode': 'adaptive',
            'max_attempts': 10
        }
    )
    dynamodb = boto3.client('dynamodb', config=config)
    return dynamodb


# ---------------------------------------------------------------------------
# 2. タイムアウト設定
# ---------------------------------------------------------------------------

def timeout_config():
    """接続タイムアウト・読み取りタイムアウトを設定する"""
    config = Config(
        connect_timeout=5,     # 接続タイムアウト（秒）
        read_timeout=10,       # 読み取りタイムアウト（秒）
        retries={'max_attempts': 3}
    )
    s3 = boto3.client('s3', config=config)
    return s3


def per_operation_timeout():
    """操作ごとにタイムアウトを変える"""
    # 小さい操作用（短めのタイムアウト）
    fast_config = Config(connect_timeout=3, read_timeout=5)

    # 大きい操作用（長めのタイムアウト）
    slow_config = Config(connect_timeout=10, read_timeout=300)

    s3_fast = boto3.client('s3', config=fast_config)   # メタデータ取得など
    s3_slow = boto3.client('s3', config=slow_config)   # 大容量ダウンロードなど

    return s3_fast, s3_slow


# ---------------------------------------------------------------------------
# 3. カスタムリトライ戦略（指数バックオフ + フルジッター）
# ---------------------------------------------------------------------------

RETRYABLE_ERRORS = [
    'ThrottlingException',
    'TooManyRequestsException',
    'ProvisionedThroughputExceededException',
    'RequestLimitExceeded',
    'ServiceUnavailable',
    'InternalServerError',
]


def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """指数バックオフ + ジッター付きリトライ"""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code not in RETRYABLE_ERRORS:
                raise  # リトライ不可能なエラー

            if attempt == max_retries:
                raise  # リトライ回数超過

            # 指数バックオフ + フルジッター
            delay = base_delay * (2 ** attempt)
            jitter = random.uniform(0, delay)
            sleep_time = jitter

            print(
                f"リトライ {attempt + 1}/{max_retries}  "
                f"待機: {sleep_time:.2f}秒  エラー: {error_code}"
            )
            time.sleep(sleep_time)


# ---------------------------------------------------------------------------
# 使用例
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    result = retry_with_backoff(
        lambda: table.get_item(
            Key={'category': 'books', 'product_id': 'b001'}
        )
    )
    print(result)
