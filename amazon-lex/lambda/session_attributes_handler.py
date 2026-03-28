# Amazon Lex #6 — セッション属性を活用した文脈の引き継ぎ
# ファイル: session_attributes_handler.py
# 概要: Amazon Connect から渡されたコンタクト属性（電話番号など）を
#       セッション属性経由で受け取り、DB 検索で顧客情報を取得。
#       顧客ランクに応じたパーソナライズ応答と、
#       Runtime Hints による音声認識精度向上を組み合わせる。

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """セッション属性を活用したインテリジェントな応答。

    Connect コンタクト属性 → Lex セッション属性 → Lambda で活用する流れ。
    """
    logger.info("Received event: %s", json.dumps(event, ensure_ascii=False))

    session_attributes = event["sessionState"].get("sessionAttributes", {})

    # Connectから渡された顧客情報
    customer_tier = session_attributes.get("customerTier", "standard")
    caller_phone = session_attributes.get("callerPhoneNumber", "")

    # 電話番号から顧客情報をDB検索
    customer = lookup_customer_by_phone(caller_phone)

    if customer:
        # 顧客の過去注文番号をRuntime Hintsとして設定
        recent_orders = customer.get("recentOrders", [])

        # セッション属性に顧客名を保存（後続の会話で利用）
        session_attributes["customerName"] = customer["name"]
        session_attributes["customerId"] = customer["id"]

        runtime_hints = build_runtime_hints(
            event["sessionState"]["intent"]["name"],
            recent_orders,
        )

        greeting = f'{customer["name"]}様、お電話ありがとうございます。'
    else:
        runtime_hints = {}
        greeting = "お電話ありがとうございます。"

    # 顧客ランクに応じた対応分岐
    if customer_tier == "premium":
        greeting += "プレミアム会員のお客様ですね。"

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
                "content": f"{greeting}ご注文番号をお教えください。",
            }
        ],
    }


# ---------------------------------------------------------------------------
# ビジネスロジック（本番では DynamoDB 等に置き換え）
# ---------------------------------------------------------------------------


def lookup_customer_by_phone(phone_number):
    """電話番号から顧客情報を検索する（簡略化）。"""
    customers = {
        "+819012345678": {
            "name": "田中",
            "id": "C-001",
            "recentOrders": ["ORD-001", "ORD-042"],
        }
    }
    return customers.get(phone_number)


def build_runtime_hints(intent_name, order_ids):
    """Runtime Hints 構造体を構築する。

    Parameters
    ----------
    intent_name : str
        対象のインテント名
    order_ids : list[str]
        ヒントとして提供する注文番号のリスト

    Returns
    -------
    dict
        Lex V2 の runtimeHints 形式
    """
    if not order_ids:
        return {}
    return {
        "slotHints": {
            intent_name: {
                "OrderId": {
                    "runtimeHintValues": [
                        {"phrase": oid} for oid in order_ids
                    ]
                }
            }
        }
    }
