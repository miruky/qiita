# ソース記事: AWS SAM #6 — REST APIアプリを構築してCI/CDパイプラインまで通してみる
# GET /items — 全アイテムを取得

import os
import logging
import boto3
from src.utils.response import api_response, error_response

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


def lambda_handler(event, context):
    """全アイテムを取得"""
    try:
        response = table.scan()
        items = response.get('Items', [])

        logger.info(f"Retrieved {len(items)} items")
        return api_response(200, {
            'items': items,
            'count': len(items)
        })

    except Exception as e:
        return error_response(500, str(e))
