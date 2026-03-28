# ソース記事: AWS SAM #1 — SAMって何？サーバーレス開発の第一歩を踏み出してみる
# Hello World Lambda関数

import json


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
        }),
    }
