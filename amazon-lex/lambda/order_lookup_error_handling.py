# Amazon Lex #3 — エラーハンドリング付きフルフィルメント
# ファイル: order_lookup_error_handling.py
# 概要: order_lookup.py の改良版。try-except によるエラーハンドリングを追加し、
#       DB 検索やAPI 呼び出しの失敗時にもユーザーに適切な応答を返す。

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Lex V2 コードフックのエントリポイント（エラーハンドリング版）。"""
    logger.info("Received event: %s", json.dumps(event, ensure_ascii=False))

    intent_name = event["sessionState"]["intent"]["name"]
    invocation_source = event["invocationSource"]

    if intent_name == "CheckOrderStatus":
        if invocation_source == "DialogCodeHook":
            return handle_dialog(event)
        elif invocation_source == "FulfillmentCodeHook":
            return handle_fulfillment(event)

    return delegate(event)


def handle_dialog(event):
    """ダイアログコードフック：スロット値のバリデーション"""
    slots = event["sessionState"]["intent"]["slots"]
    order_id_slot = slots.get("OrderId")

    if not order_id_slot or not order_id_slot.get("value"):
        return delegate(event)

    order_id = order_id_slot["value"]["interpretedValue"]

    if not order_id.startswith("ORD-"):
        return elicit_slot(
            event,
            "OrderId",
            "注文番号はORD-で始まる形式です（例：ORD-001）。もう一度お教えください。",
        )

    return delegate(event)


def handle_fulfillment(event):
    """エラーハンドリング付きフルフィルメント。

    DB 検索やAPI 呼び出し失敗時にもユーザーフレンドリーな応答を返す。
    """
    try:
        slots = event["sessionState"]["intent"]["slots"]
        order_id = slots["OrderId"]["value"]["interpretedValue"]

        # DB検索処理（実際にはDynamoDBなどを使用）
        order = lookup_order(order_id)

        if order:
            message = format_order_response(order_id, order)
        else:
            message = f"注文番号 {order_id} は見つかりませんでした。"

    except Exception as e:
        logger.error("Error: %s", str(e))
        message = (
            "申し訳ございません。システムエラーが発生しました。"
            "お手数ですが、しばらく時間をおいてから再度お試しください。"
        )

    return close(event, "Fulfilled", message)


# ---------------------------------------------------------------------------
# ビジネスロジック（本番では DynamoDB 等に置き換え）
# ---------------------------------------------------------------------------

ORDERS = {
    "ORD-001": {
        "customerName": "田中太郎",
        "product": "ワイヤレスイヤホン",
        "status": "配送中",
        "estimatedDelivery": "2026年3月10日",
    },
    "ORD-002": {
        "customerName": "佐藤花子",
        "product": "モバイルバッテリー",
        "status": "出荷準備中",
        "estimatedDelivery": "2026年3月12日",
    },
    "ORD-003": {
        "customerName": "鈴木一郎",
        "product": "USBケーブル",
        "status": "お届け済み",
        "estimatedDelivery": "2026年3月5日",
    },
}


def lookup_order(order_id):
    """注文情報を検索する（本番では DynamoDB を使用）。"""
    return ORDERS.get(order_id)


def format_order_response(order_id, order):
    """注文情報を応答メッセージに整形する。"""
    return (
        f"注文番号 {order_id} の情報です。\n"
        f"商品：{order['product']}\n"
        f"ステータス：{order['status']}\n"
        f"お届け予定日：{order['estimatedDelivery']}"
    )


# ---------------------------------------------------------------------------
# ヘルパー関数 — Lex V2 レスポンスビルダー
# ---------------------------------------------------------------------------


def delegate(event):
    """Lexにダイアログ管理を委任する"""
    return {
        "sessionState": {
            "dialogAction": {"type": "Delegate"},
            "intent": event["sessionState"]["intent"],
        }
    }


def elicit_slot(event, slot_name, message):
    """特定のスロットを再度引き出す"""
    return {
        "sessionState": {
            "dialogAction": {
                "type": "ElicitSlot",
                "slotToElicit": slot_name,
            },
            "intent": event["sessionState"]["intent"],
        },
        "messages": [
            {"contentType": "PlainText", "content": message}
        ],
    }


def close(event, fulfillment_state, message):
    """会話を終了する"""
    return {
        "sessionState": {
            "dialogAction": {"type": "Close"},
            "intent": {
                "name": event["sessionState"]["intent"]["name"],
                "state": fulfillment_state,
            },
        },
        "messages": [
            {"contentType": "PlainText", "content": message}
        ],
    }
