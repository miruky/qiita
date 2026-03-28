"""
AWS SDK (Boto3) シリーズ #4
DynamoDB テーブルの作成と管理（GSI 付き含む）
"""

import boto3


def create_table():
    """テーブルを作成する"""
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')

    table = dynamodb.create_table(
        TableName='Products',
        KeySchema=[
            {'AttributeName': 'category', 'KeyType': 'HASH'},    # パーティションキー
            {'AttributeName': 'product_id', 'KeyType': 'RANGE'}  # ソートキー
        ],
        AttributeDefinitions=[
            {'AttributeName': 'category', 'AttributeType': 'S'},
            {'AttributeName': 'product_id', 'AttributeType': 'S'},
        ],
        BillingMode='PAY_PER_REQUEST'  # オンデマンドモード
    )

    table.wait_until_exists()
    print(f"テーブル '{table.table_name}' を作成しました")
    print(f"ステータス: {table.table_status}")


def describe_table():
    """テーブル情報を取得する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    table.load()

    print(f"テーブル名:   {table.table_name}")
    print(f"ステータス:   {table.table_status}")
    print(f"アイテム数:   {table.item_count}")
    print(f"サイズ:       {table.table_size_bytes} bytes")
    print(f"キースキーマ: {table.key_schema}")
    print(f"作成日時:     {table.creation_date_time}")


def list_tables():
    """テーブル一覧を取得する"""
    dynamodb = boto3.client('dynamodb')

    response = dynamodb.list_tables()
    for name in response['TableNames']:
        print(name)


def create_table_with_gsi():
    """GSI（グローバルセカンダリインデックス）付きテーブルを作成する"""
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='Orders',
        KeySchema=[
            {'AttributeName': 'order_id', 'KeyType': 'HASH'},
        ],
        AttributeDefinitions=[
            {'AttributeName': 'order_id', 'AttributeType': 'S'},
            {'AttributeName': 'customer_id', 'AttributeType': 'S'},
            {'AttributeName': 'order_date', 'AttributeType': 'S'},
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'CustomerIndex',
                'KeySchema': [
                    {'AttributeName': 'customer_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'order_date', 'KeyType': 'RANGE'},
                ],
                'Projection': {'ProjectionType': 'ALL'},
            },
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    table.wait_until_exists()
    print("GSI 付きテーブルを作成しました")
