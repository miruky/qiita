# Amazon Lex #3 — Lambda連携で動的な応答を返すボット
# ファイル: order_lookup.py
# 概要: Lex V2 の CheckOrderStatus インテント用 Lambda 関数。
#       ダイアログコードフックで注文番号のバリデーション、
#       フルフィルメントコードフックで注文情報の検索・応答を行う。

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# サンプルの注文データ（本番ではDynamoDB等から取得）
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


def lambda_handler(event, context):
    """Lex V2 コードフックのエントリポイント。

    invocationSource に応じてダイアログ / フルフィルメント処理を振り分ける。
    """
    logger.info("Received event: %s", json.dumps(event, ensure_ascii=False))

    intent_name = event["sessionState"]["intent"]["name"]
    invocation_source = event["invocationSource"]  # DialogCodeHook or FulfillmentCodeHook

    if intent_name == "CheckOrderStatus":
        if invocation_source == "DialogCodeHook":
            return handle_dialog(event)
        elif invocation_source == "FulfillmentCodeHook":
            return handle_fulfillment(event)

    # その他のインテントはそのまま通過
    return delegate(event)


def handle_dialog(event):
    """ダイアログコードフック：スロット値のバリデーション"""
    slots = event["sessionState"]["intent"]["slots"]
    order_id_slot = slots.get("OrderId")

    # スロットがまだ埋まっていない場合はLexに委任
    if not order_id_slot or not order_id_slot.get("value"):
        return delegate(event)

    order_id = order_id_slot["value"]["interpretedValue"]

    # 注文番号の形式チェック（ORD-で始まるか）
    if not order_id.startswith("ORD-"):
        return elicit_slot(
            event,
            "OrderId",
            "注文番号はORD-で始まる形式です（例：ORD-001）。もう一度お教えください。",
        )

    return delegate(event)


def handle_fulfillment(event):
    """フルフィルメントコードフック：注文情報の検索と応答"""
    slots = event["sessionState"]["intent"]["slots"]
    order_id = slots["OrderId"]["value"]["interpretedValue"]

    if order_id in ORDERS:
        order = ORDERS[order_id]
        message = (
            f"注文番号 {order_id} の情報です。\n"
            f"商品：{order['product']}\n"
            f"ステータス：{order['status']}\n"
            f"お届け予定日：{order['estimatedDelivery']}"
        )
    else:
        message = (
            f"注文番号 {order_id} は見つかりませんでした。"
            "番号をご確認の上、もう一度お試しください。"
        )

    return close(event, "Fulfilled", message)


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
