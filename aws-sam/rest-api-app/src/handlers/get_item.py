# ソース記事: AWS SAM #6 — REST APIアプリを構築してCI/CDパイプラインまで通してみる
# GET /items/{id} — IDでアイテムを取得

import os
import logging
import boto3
from src.utils.response import api_response, error_response

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


def lambda_handler(event, context):
    """IDでアイテムを取得"""
    try:
        item_id = event['pathParameters']['id']

        response = table.get_item(Key={'id': item_id})
        item = response.get('Item')

        if not item:
            return error_response(404, f'Item {item_id} not found')

        logger.info(f"Retrieved item: {item_id}")
        return api_response(200, {'item': item})

    except Exception as e:
        return error_response(500, str(e))
