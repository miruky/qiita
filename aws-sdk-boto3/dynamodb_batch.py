"""
AWS SDK (Boto3) シリーズ #4
DynamoDB のバッチ書き込み・バッチ読み込み・バッチ削除
"""

from decimal import Decimal

import boto3


def batch_write():
    """batch_writer でまとめて書き込む"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    products = [
        {'category': 'books', 'product_id': 'b001', 'name': 'Python入門', 'price': Decimal('2800')},
        {'category': 'books', 'product_id': 'b002', 'name': 'AWS実践ガイド', 'price': Decimal('3500')},
        {'category': 'books', 'product_id': 'b003', 'name': 'Docker入門', 'price': Decimal('2400')},
        {'category': 'electronics', 'product_id': 'p002', 'name': 'USBメモリ', 'price': Decimal('1200')},
        {'category': 'electronics', 'product_id': 'p003', 'name': 'マウスパッド', 'price': Decimal('800')},
    ]

    # batch_writer は自動で 25 件ずつバッチリクエストに分割
    with table.batch_writer() as batch:
        for product in products:
            batch.put_item(Item=product)

    print(f"{len(products)} 件を書き込みました")


def batch_read():
    """batch_get_item で複数テーブルから一括取得する"""
    dynamodb = boto3.resource('dynamodb')

    response = dynamodb.batch_get_item(
        RequestItems={
            'Products': {
                'Keys': [
                    {'category': 'books', 'product_id': 'b001'},
                    {'category': 'books', 'product_id': 'b002'},
                    {'category': 'electronics', 'product_id': 'p002'},
                ]
            }
        }
    )

    for item in response['Responses']['Products']:
        print(f"{item['name']}  ¥{item['price']}")


def batch_delete():
    """batch_writer でまとめて削除する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    keys_to_delete = [
        {'category': 'books', 'product_id': 'b001'},
        {'category': 'books', 'product_id': 'b002'},
        {'category': 'books', 'product_id': 'b003'},
    ]

    with table.batch_writer() as batch:
        for key in keys_to_delete:
            batch.delete_item(Key=key)

    print(f"{len(keys_to_delete)} 件を削除しました")
