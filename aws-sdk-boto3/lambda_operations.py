"""
AWS SDK (Boto3) シリーズ #5
Lambda 関数の作成・同期/非同期呼び出し・更新

NOTE: Lambda ランタイムは python3.12 を使用（記事原文を修正済み）
"""

import io
import json
import zipfile

import boto3


def list_functions():
    """Lambda 関数の一覧を取得する"""
    client = boto3.client('lambda', region_name='ap-northeast-1')

    response = client.list_functions()
    for func in response['Functions']:
        print(f"{func['FunctionName']}  "
              f"ランタイム: {func['Runtime']}  "
              f"メモリ: {func['MemorySize']}MB")


def invoke_sync():
    """同期呼び出し（RequestResponse）"""
    client = boto3.client('lambda')

    payload = {
        'name': '田中太郎',
        'action': 'greet'
    }

    response = client.invoke(
        FunctionName='my-hello-function',
        InvocationType='RequestResponse',  # 同期呼び出し
        Payload=json.dumps(payload)
    )

    result = json.loads(response['Payload'].read())
    print(f"ステータスコード: {response['StatusCode']}")
    print(f"レスポンス: {result}")


def invoke_async():
    """非同期呼び出し（Event）"""
    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName='my-async-processor',
        InvocationType='Event',  # 非同期（202 が返って終了）
        Payload=json.dumps({'task': 'process_data', 'id': 12345})
    )

    print(f"ステータスコード: {response['StatusCode']}")  # 202


def invoke_dryrun():
    """DryRun（権限チェック）"""
    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName='my-hello-function',
        InvocationType='DryRun',  # 実行せず権限チェックのみ
        Payload=json.dumps({})
    )
    print(f"ステータスコード: {response['StatusCode']}")  # 204


def create_function():
    """Lambda 関数を作成する"""
    # Lambda 用のコードを ZIP に固める
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr('lambda_function.py', '''
def lambda_handler(event, context):
    name = event.get('name', 'World')
    return {
        'statusCode': 200,
        'body': f'Hello, {name}!'
    }
''')
    zip_buffer.seek(0)

    client = boto3.client('lambda')

    response = client.create_function(
        FunctionName='my-hello-function',
        Runtime='python3.12',
        Role='arn:aws:iam::123456789012:role/lambda-execution-role',
        Handler='lambda_function.lambda_handler',
        Code={'ZipFile': zip_buffer.read()},
        Timeout=30,
        MemorySize=128,
        Environment={
            'Variables': {
                'ENV': 'production',
                'LOG_LEVEL': 'INFO'
            }
        }
    )
    print(f"作成: {response['FunctionName']}  ARN: {response['FunctionArn']}")


def update_function():
    """Lambda 関数の設定を更新する"""
    client = boto3.client('lambda')

    client.update_function_configuration(
        FunctionName='my-hello-function',
        Timeout=60,
        MemorySize=256,
        Environment={
            'Variables': {
                'ENV': 'staging',
                'LOG_LEVEL': 'DEBUG'
            }
        }
    )
