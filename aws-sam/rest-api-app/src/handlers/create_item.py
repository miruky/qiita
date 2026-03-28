# ソース記事: AWS SAM #6 — REST APIアプリを構築してCI/CDパイプラインまで通してみる
# POST /items — 新しいアイテムを作成

import os
import json
import uuid
import logging
from datetime import datetime, timezone
import boto3
from src.utils.response import api_response, error_response

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


def lambda_handler(event, context):
    """新しいアイテムを作成"""
    try:
        body = json.loads(event.get('body', '{}'))

        if 'name' not in body:
            return error_response(400, 'name is required')

        item = {
            'id': str(uuid.uuid4()),
            'name': body['name'],
            'description': body.get('description', ''),
            'price': body.get('price', 0),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }

        table.put_item(Item=item)

        logger.info(f"Created item: {item['id']}")
        return api_response(201, {'item': item})

    except json.JSONDecodeError:
        return error_response(400, 'Invalid JSON body')
    except Exception as e:
        return error_response(500, str(e))
