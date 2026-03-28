# ソース記事: AWS SAM #6 — REST APIアプリを構築してCI/CDパイプラインまで通してみる
# レスポンスヘルパー

import json
import logging

logger = logging.getLogger()


def api_response(status_code: int, body: dict) -> dict:
    """API Gatewayレスポンスを生成"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        },
        'body': json.dumps(body, ensure_ascii=False, default=str)
    }


def error_response(status_code: int, message: str) -> dict:
    """エラーレスポンスを生成"""
    logger.error(f"Error {status_code}: {message}")
    return api_response(status_code, {'error': message})
