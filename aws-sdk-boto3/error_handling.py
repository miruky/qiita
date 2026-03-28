"""
AWS SDK (Boto3) シリーズ #6
エラーハンドリングの基本パターン
"""

import logging

import boto3
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    ConnectTimeoutError,
    EndpointConnectionError,
    NoCredentialsError,
    ReadTimeoutError,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. ClientError のハンドリング
# ---------------------------------------------------------------------------

def handle_client_error():
    """ClientError のレスポンスからエラーコード・メッセージを取得する"""
    s3 = boto3.client('s3')

    try:
        s3.head_bucket(Bucket='my-bucket')
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']

        print(f"エラーコード: {error_code}")
        print(f"メッセージ:   {error_message}")
        print(f"HTTPステータス: {status_code}")

        if error_code in ('404', 'NoSuchBucket'):
            print("バケットが存在しません")
        elif error_code == '403':
            print("アクセス権限がありません")
        else:
            raise


# ---------------------------------------------------------------------------
# 2. サービス固有の例外
# ---------------------------------------------------------------------------

def handle_service_exceptions():
    """クライアントに紐付くサービス固有例外を使う"""
    s3 = boto3.client('s3')

    try:
        s3.get_object(Bucket='my-bucket', Key='missing.txt')
    except s3.exceptions.NoSuchKey:
        print("オブジェクトが見つかりません")
    except s3.exceptions.NoSuchBucket:
        print("バケットが存在しません")


# ---------------------------------------------------------------------------
# 3. BotoCoreError のハンドリング（SDK 内部エラー）
# ---------------------------------------------------------------------------

def handle_botocore_errors():
    """SDK 内部エラーを種類ごとにハンドリングする"""
    try:
        s3 = boto3.client('s3')
        s3.list_buckets()
    except NoCredentialsError:
        print("認証情報が見つかりません。aws configure を実行してください")
    except EndpointConnectionError:
        print("AWS エンドポイントに接続できません。ネットワークを確認してください")
    except ReadTimeoutError:
        print("レスポンスの読み取りがタイムアウトしました")
    except ConnectTimeoutError:
        print("接続がタイムアウトしました")
    except ClientError as e:
        print(f"AWS API エラー: {e.response['Error']['Code']}")
    except BotoCoreError as e:
        print(f"SDK エラー: {e}")


# ---------------------------------------------------------------------------
# 4. 包括的なエラーハンドリングパターン
# ---------------------------------------------------------------------------

def safe_s3_get(bucket: str, key: str) -> bytes | None:
    """S3 からオブジェクトを安全に取得する"""
    s3 = boto3.client('s3')

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()

    except ClientError as e:
        code = e.response['Error']['Code']
        if code == 'NoSuchKey':
            logger.warning(f"オブジェクトが見つかりません: s3://{bucket}/{key}")
            return None
        elif code == 'AccessDenied':
            logger.error(f"アクセス拒否: s3://{bucket}/{key}")
            raise PermissionError(f"S3 アクセス拒否: {key}") from e
        else:
            logger.error(
                f"S3 エラー [{code}]: {e.response['Error']['Message']}"
            )
            raise

    except BotoCoreError as e:
        logger.error(f"SDK 内部エラー: {e}")
        raise


# ---------------------------------------------------------------------------
# 5. レスポンスメタデータの確認
# ---------------------------------------------------------------------------

def check_response_metadata():
    """レスポンスに含まれるメタデータを確認する"""
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    metadata = response['ResponseMetadata']
    print(f"HTTP ステータス: {metadata['HTTPStatusCode']}")
    print(f"リクエスト ID:   {metadata['RequestId']}")
    print(f"リトライ回数:   {metadata['RetryAttempts']}")
