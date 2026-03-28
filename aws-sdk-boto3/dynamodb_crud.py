"""
AWS SDK (Boto3) シリーズ #4
DynamoDB の Put / Get / Update / Delete 操作
"""

from decimal import Decimal

import boto3
from botocore.exceptions import ClientError


# =============================================================
# Put（書き込み）
# =============================================================

def put_item():
    """アイテムを追加する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    table.put_item(
        Item={
            'category': 'electronics',
            'product_id': 'p001',
            'name': 'ワイヤレスイヤホン',
            'price': Decimal('4980'),
            'stock': 150,
            'tags': ['audio', 'bluetooth', 'wireless'],
            'specs': {
                'battery': '8時間',
                'weight': '5.4g',
                'color': ['black', 'white']
            }
        }
    )


def put_item_conditional():
    """条件付き Put（既存の場合は上書きしない）"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    try:
        table.put_item(
            Item={
                'category': 'electronics',
                'product_id': 'p001',
                'name': 'ワイヤレスイヤホン',
                'price': Decimal('4980'),
            },
            ConditionExpression='attribute_not_exists(product_id)'
        )
        print("新規アイテムを追加しました")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print("アイテムは既に存在します")
        else:
            raise


# =============================================================
# Get（取得）
# =============================================================

def get_item():
    """アイテムを取得する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.get_item(
        Key={
            'category': 'electronics',
            'product_id': 'p001'
        }
    )

    item = response.get('Item')
    if item:
        print(f"商品名: {item['name']}")
        print(f"価格:   {item['price']}円")
        print(f"在庫:   {item['stock']}個")
    else:
        print("アイテムが見つかりません")


def get_item_projection():
    """特定の属性のみ取得する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.get_item(
        Key={
            'category': 'electronics',
            'product_id': 'p001'
        },
        ProjectionExpression='#n, price, stock',
        ExpressionAttributeNames={'#n': 'name'}  # name は予約語
    )

    item = response['Item']
    print(f"{item['name']}  ¥{item['price']}  在庫: {item['stock']}")


def get_item_consistent():
    """強い整合性読み込み"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.get_item(
        Key={
            'category': 'electronics',
            'product_id': 'p001'
        },
        ConsistentRead=True  # 強い整合性（コスト 2 倍）
    )
    return response.get('Item')


# =============================================================
# Update（更新）
# =============================================================

def update_item():
    """アイテムを更新する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.update_item(
        Key={
            'category': 'electronics',
            'product_id': 'p001'
        },
        UpdateExpression='SET price = :p, stock = :s',
        ExpressionAttributeValues={
            ':p': Decimal('3980'),
            ':s': 200
        },
        ReturnValues='ALL_NEW'
    )

    updated = response['Attributes']
    print(f"更新後の価格: {updated['price']}円")
    print(f"更新後の在庫: {updated['stock']}個")


def update_item_increment():
    """数値のインクリメント・デクリメント"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    # 在庫を 10 個減らす
    table.update_item(
        Key={
            'category': 'electronics',
            'product_id': 'p001'
        },
        UpdateExpression='SET stock = stock - :val',
        ExpressionAttributeValues={':val': 10},
        ConditionExpression='stock >= :val'  # 在庫が足りること
    )


def update_item_nested():
    """リスト・マップ内の値を操作する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    # タグを追加
    table.update_item(
        Key={'category': 'electronics', 'product_id': 'p001'},
        UpdateExpression='SET tags = list_append(tags, :new_tags)',
        ExpressionAttributeValues={
            ':new_tags': ['sale', 'popular']
        }
    )

    # マップ内の値を更新
    table.update_item(
        Key={'category': 'electronics', 'product_id': 'p001'},
        UpdateExpression='SET specs.battery = :b',
        ExpressionAttributeValues={
            ':b': '10時間'
        }
    )

    # 属性を削除
    table.update_item(
        Key={'category': 'electronics', 'product_id': 'p001'},
        UpdateExpression='REMOVE old_attribute'
    )


# =============================================================
# Delete（削除）
# =============================================================

def delete_item():
    """アイテムを削除する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    table.delete_item(
        Key={
            'category': 'electronics',
            'product_id': 'p001'
        }
    )
    print("アイテムを削除しました")


def delete_item_return_old():
    """削除前の値を取得する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.delete_item(
        Key={
            'category': 'electronics',
            'product_id': 'p001'
        },
        ReturnValues='ALL_OLD'
    )

    deleted = response.get('Attributes')
    if deleted:
        print(f"削除したアイテム: {deleted['name']}")


def delete_item_conditional():
    """条件付き削除"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    try:
        table.delete_item(
            Key={
                'category': 'electronics',
                'product_id': 'p001'
            },
            ConditionExpression='stock = :zero',
            ExpressionAttributeValues={':zero': 0}
        )
        print("在庫ゼロの商品を削除しました")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print("在庫が残っているため削除できません")
        else:
            raise
