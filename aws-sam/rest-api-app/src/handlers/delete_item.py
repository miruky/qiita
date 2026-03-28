# ソース記事: AWS SAM #6 — REST APIアプリを構築してCI/CDパイプラインまで通してみる
# DELETE /items/{id} — アイテムを削除

import os
import logging
import boto3
from src.utils.response import api_response, error_response

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


def lambda_handler(event, context):
    """アイテムを削除"""
    try:
        item_id = event['pathParameters']['id']

        table.delete_item(Key={'id': item_id})

        logger.info(f"Deleted item: {item_id}")
        return api_response(200, {'message': f'Item {item_id} deleted'})

    except Exception as e:
        return error_response(500, str(e))
