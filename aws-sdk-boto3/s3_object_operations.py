"""
AWS SDK (Boto3) シリーズ #3
S3 オブジェクトのアップロード・ダウンロード・コピー・削除
"""

import json
import os

import boto3


# =============================================================
# オブジェクトのアップロード
# =============================================================

def upload_text_and_json():
    """テキスト・JSON データのアップロード"""
    s3 = boto3.client('s3')

    # テキストデータ
    s3.put_object(
        Bucket='my-bucket',
        Key='data/hello.txt',
        Body='Hello, Boto3!'.encode('utf-8'),
        ContentType='text/plain'
    )

    # JSON データ
    data = {'name': 'miruky', 'service': 'S3'}
    s3.put_object(
        Bucket='my-bucket',
        Key='data/info.json',
        Body=json.dumps(data, ensure_ascii=False).encode('utf-8'),
        ContentType='application/json'
    )


def upload_files():
    """ファイルのアップロード"""
    s3 = boto3.client('s3')

    # upload_file（ファイルパス指定）
    s3.upload_file(
        Filename='local_image.png',
        Bucket='my-bucket',
        Key='images/image.png'
    )

    # upload_fileobj（ファイルオブジェクト指定）
    with open('report.pdf', 'rb') as f:
        s3.upload_fileobj(
            Fileobj=f,
            Bucket='my-bucket',
            Key='reports/report.pdf'
        )


def upload_with_metadata():
    """メタデータ・タグ付きアップロード"""
    s3 = boto3.client('s3')

    s3.put_object(
        Bucket='my-bucket',
        Key='data/document.txt',
        Body=b'Important document',
        ContentType='text/plain',
        Metadata={
            'author': 'miruky',
            'version': '1.0',
            'department': 'engineering'
        },
        Tagging='project=demo&env=dev'
    )


def upload_with_progress():
    """コールバックで進捗表示する Resource 版アップロード"""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('my-bucket')

    file_size = os.path.getsize('large_file.zip')
    uploaded = 0

    def progress_callback(bytes_transferred):
        nonlocal uploaded
        uploaded += bytes_transferred
        percent = (uploaded / file_size) * 100
        print(f"\r{percent:.1f}% ({uploaded}/{file_size} bytes)", end='')

    bucket.upload_file(
        'large_file.zip',
        'backups/large_file.zip',
        Callback=progress_callback
    )
    print("\nアップロード完了")


# =============================================================
# オブジェクトのダウンロード
# =============================================================

def download_files():
    """ファイルとしてダウンロードする"""
    s3 = boto3.client('s3')

    # download_file
    s3.download_file(
        Bucket='my-bucket',
        Key='data/hello.txt',
        Filename='downloaded_hello.txt'
    )

    # download_fileobj
    with open('downloaded.pdf', 'wb') as f:
        s3.download_fileobj(
            Bucket='my-bucket',
            Key='reports/report.pdf',
            Fileobj=f
        )


def download_to_memory():
    """メモリ上に読み込む"""
    s3 = boto3.client('s3')

    # テキストとして読み込み
    response = s3.get_object(Bucket='my-bucket', Key='data/hello.txt')
    content = response['Body'].read().decode('utf-8')
    print(content)

    # JSON として読み込み
    response = s3.get_object(Bucket='my-bucket', Key='data/info.json')
    data = json.loads(response['Body'].read())
    print(data['name'])

    # メタデータの取得
    print(f"Content-Type: {response['ContentType']}")
    print(f"Last-Modified: {response['LastModified']}")
    print(f"Content-Length: {response['ContentLength']}")


def download_partial():
    """範囲指定で一部だけ取得する"""
    s3 = boto3.client('s3')

    response = s3.get_object(
        Bucket='my-bucket',
        Key='data/large_file.csv',
        Range='bytes=0-99'
    )
    first_100_bytes = response['Body'].read()
    return first_100_bytes


# =============================================================
# オブジェクトの一覧・検索
# =============================================================

def list_objects():
    """オブジェクト一覧を取得する"""
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket='my-bucket')
    for obj in response.get('Contents', []):
        print(f"{obj['Key']}  ({obj['Size']} bytes)  {obj['LastModified']}")


def list_objects_with_prefix():
    """プレフィックスでフィルタリングする"""
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(
        Bucket='my-bucket',
        Prefix='images/'
    )
    for obj in response.get('Contents', []):
        print(obj['Key'])


def list_all_objects_paginator():
    """Paginator で全件取得する"""
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    total_size = 0
    total_count = 0

    for page in paginator.paginate(Bucket='my-bucket', Prefix='logs/'):
        for obj in page.get('Contents', []):
            total_size += obj['Size']
            total_count += 1

    print(f"合計: {total_count} ファイル, {total_size / 1024 / 1024:.2f} MB")


def list_objects_resource():
    """Resource 版でオブジェクトを一覧する"""
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('my-bucket')

    # 全オブジェクト（ページネーション自動）
    for obj in bucket.objects.all():
        print(f"{obj.key}  ({obj.size} bytes)")

    # プレフィックスでフィルタ
    for obj in bucket.objects.filter(Prefix='images/'):
        print(obj.key)


# =============================================================
# オブジェクトのコピー・削除
# =============================================================

def copy_objects():
    """オブジェクトをコピーする"""
    s3 = boto3.client('s3')

    # 同じバケット内でコピー
    s3.copy_object(
        CopySource={'Bucket': 'my-bucket', 'Key': 'data/original.txt'},
        Bucket='my-bucket',
        Key='data/backup/original_backup.txt'
    )

    # 別のバケットへコピー
    s3.copy_object(
        CopySource={'Bucket': 'source-bucket', 'Key': 'file.txt'},
        Bucket='destination-bucket',
        Key='file.txt'
    )


def delete_objects():
    """オブジェクトを削除する"""
    s3 = boto3.client('s3')

    # 単一オブジェクトの削除
    s3.delete_object(
        Bucket='my-bucket',
        Key='data/old_file.txt'
    )

    # 複数オブジェクトの一括削除
    s3.delete_objects(
        Bucket='my-bucket',
        Delete={
            'Objects': [
                {'Key': 'data/file1.txt'},
                {'Key': 'data/file2.txt'},
                {'Key': 'data/file3.txt'},
            ]
        }
    )


def delete_prefix():
    """プレフィックス配下を全削除する"""
    s3 = boto3.client('s3')

    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket='my-bucket', Prefix='temp/'):
        if 'Contents' not in page:
            continue

        objects = [{'Key': obj['Key']} for obj in page['Contents']]
        s3.delete_objects(
            Bucket='my-bucket',
            Delete={'Objects': objects}
        )

    print("temp/ 配下を全削除しました")
