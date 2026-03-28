# ソース記事: AWS SAM #6 — REST APIアプリを構築してCI/CDパイプラインまで通してみる
# PUT /items/{id} — アイテムを更新

import os
import json
import logging
from datetime import datetime, timezone
import boto3
from src.utils.response import api_response, error_response

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


def lambda_handler(event, context):
    """アイテムを更新"""
    try:
        item_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))

        # アイテムの存在確認
        existing = table.get_item(Key={'id': item_id})
        if 'Item' not in existing:
            return error_response(404, f'Item {item_id} not found')

        # 更新式を動的に構築
        update_parts = []
        expression_values = {}
        expression_names = {}

        for key in ['name', 'description', 'price']:
            if key in body:
                update_parts.append(f'#{key} = :{key}')
                expression_values[f':{key}'] = body[key]
                expression_names[f'#{key}'] = key

        update_parts.append('#updated_at = :updated_at')
        expression_values[':updated_at'] = datetime.now(timezone.utc).isoformat()
        expression_names['#updated_at'] = 'updated_at'

        response = table.update_item(
            Key={'id': item_id},
            UpdateExpression='SET ' + ', '.join(update_parts),
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names,
            ReturnValues='ALL_NEW'
        )

        logger.info(f"Updated item: {item_id}")
        return api_response(200, {'item': response['Attributes']})

    except json.JSONDecodeError:
        return error_response(400, 'Invalid JSON body')
    except Exception as e:
        return error_response(500, str(e))
