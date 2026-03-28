# Amazon Lex #6 — Runtime Hints API による動的な音声認識ヒント
# ファイル: runtime_hints_handler.py
# 概要: Lambda コードフックから Lex V2 の Runtime Hints API を利用して、
#       ASR に対してセッション固有の認識ヒントを動的に提供する。
#       例: リピーター顧客の過去の注文番号をヒントとして設定し、認識精度を向上させる。

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Runtime Hintsを設定するLambda関数。

    顧客の過去の注文番号をDBから検索し、
    それらを Runtime Hints として Lex に渡す。
    """
    logger.info("Received event: %s", json.dumps(event, ensure_ascii=False))

    intent_name = event["sessionState"]["intent"]["name"]
    session_attributes = event["sessionState"].get("sessionAttributes", {})

    # 顧客IDから過去の注文番号をDBで検索した想定
    recent_order_ids = ["ORD-001", "ORD-042", "ORD-108"]

    # Runtime Hintsの構築
    runtime_hints = {
        "slotHints": {
            intent_name: {
                "OrderId": {
                    "runtimeHintValues": [
                        {"phrase": order_id} for order_id in recent_order_ids
                    ]
                }
            }
        }
    }

    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": "OrderId",
            },
            "intent": event["sessionState"]["intent"],
            "sessionAttributes": session_attributes,
            "runtimeHints": runtime_hints,
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": "ご注文番号をお教えください。",
            }
        ],
    }
