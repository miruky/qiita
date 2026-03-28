"""
AWS SDK (Boto3) シリーズ #4
DynamoDB の Query・Scan・パラレル Scan
"""

from concurrent.futures import ThreadPoolExecutor

import boto3
from boto3.dynamodb.conditions import Attr, Key


# =============================================================
# Query：キーで検索
# =============================================================

def query_by_partition_key():
    """パーティションキーで検索する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.query(
        KeyConditionExpression=Key('category').eq('electronics')
    )

    print(f"ヒット数: {response['Count']}")
    for item in response['Items']:
        print(f"  {item['product_id']}: {item['name']}  ¥{item['price']}")


def query_with_sort_key():
    """ソートキーで範囲指定する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    # product_id が p001〜p010 の範囲
    response = table.query(
        KeyConditionExpression=(
            Key('category').eq('electronics') &
            Key('product_id').between('p001', 'p010')
        )
    )

    # product_id が p で始まる
    response = table.query(
        KeyConditionExpression=(
            Key('category').eq('electronics') &
            Key('product_id').begins_with('p')
        )
    )
    return response


def query_with_filter():
    """フィルタ条件を追加する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.query(
        KeyConditionExpression=Key('category').eq('electronics'),
        FilterExpression=Attr('price').lt(5000) & Attr('stock').gt(0)
    )

    for item in response['Items']:
        print(f"  {item['name']}  ¥{item['price']}  在庫: {item['stock']}")


def query_gsi():
    """GSI（グローバルセカンダリインデックス）へ Query する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Orders')

    response = table.query(
        IndexName='CustomerIndex',
        KeyConditionExpression=(
            Key('customer_id').eq('c001') &
            Key('order_date').begins_with('2026-03')
        )
    )

    for item in response['Items']:
        print(f"注文: {item['order_id']}  日付: {item['order_date']}")


def query_descending():
    """降順・件数制限で取得する"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.query(
        KeyConditionExpression=Key('category').eq('electronics'),
        ScanIndexForward=False,  # 降順
        Limit=5                  # 最大 5 件
    )
    return response


def query_with_pagination():
    """ページネーション付き Query"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    items = []
    last_key = None

    while True:
        params = {
            'KeyConditionExpression': Key('category').eq('electronics')
        }
        if last_key:
            params['ExclusiveStartKey'] = last_key

        response = table.query(**params)
        items.extend(response['Items'])

        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break

    print(f"合計: {len(items)} アイテム")
    return items


# =============================================================
# Scan：全件走査
# =============================================================

def scan_basic():
    """基本的な Scan"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.scan()
    for item in response['Items']:
        print(f"{item['category']}/{item['product_id']}: {item['name']}")


def scan_with_filter():
    """フィルタ付き Scan"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')

    response = table.scan(
        FilterExpression=Attr('price').between(1000, 5000)
    )
    return response


def parallel_scan():
    """パラレル Scan（大量データの高速取得）"""

    def scan_segment(segment, total_segments):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Products')

        items = []
        last_key = None

        while True:
            params = {
                'Segment': segment,
                'TotalSegments': total_segments,
            }
            if last_key:
                params['ExclusiveStartKey'] = last_key

            response = table.scan(**params)
            items.extend(response['Items'])

            last_key = response.get('LastEvaluatedKey')
            if not last_key:
                break

        return items

    # 4 セグメントで並列 Scan
    total_segments = 4
    all_items = []

    with ThreadPoolExecutor(max_workers=total_segments) as executor:
        futures = [
            executor.submit(scan_segment, seg, total_segments)
            for seg in range(total_segments)
        ]
        for future in futures:
            all_items.extend(future.result())

    print(f"合計: {len(all_items)} アイテム")
    return all_items
