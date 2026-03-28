# Amazon Lex #5 — 信頼度スコアを活用した音声認識精度の向上
# ファイル: confidence_score_handler.py
# 概要: NLU 信頼度スコアと ASR 文字起こし信頼度スコアを参照し、
#       スコアが低い場合はユーザーに再入力を求めるダイアログコードフック。
#
# 修正点（元記事からの変更）:
#   - elicit_intent() は Lex V2 の標準的なパターンではないため
#     elicit_slot() に置換し、ユーザーに再入力を促す形に変更
#   - nluConfidence はオブジェクト形式（{"score": 0.xx}）で返されるため
#     event["interpretations"][0]["nluConfidence"]["score"] でアクセスするよう修正

import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Lex V2 コードフックのエントリポイント。"""
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
    """信頼度スコアに基づくバリデーション。

    NLU 信頼度スコアと ASR 文字起こし信頼度スコアを確認し、
    閾値を下回る場合はユーザーに再入力を求める。
    """

    # NLU信頼度スコアの取得
    interpretations = event.get("interpretations", [])
    if interpretations:
        top_intent = interpretations[0]
        # nluConfidence はオブジェクト {"score": float} で返される
        nlu_confidence = top_intent.get("nluConfidence", {}).get("score", 0)

        # 信頼度が低い場合はユーザーに再入力を促す
        if nlu_confidence < 0.7:
            return elicit_slot(
                event,
                "OrderId",
                "うまく聞き取れませんでした。注文の確認でしたら、注文番号をお教えください。",
            )

    # ASR文字起こし信頼度スコアの取得
    transcriptions = event.get("transcriptions", [])
    if transcriptions:
        top_transcription = transcriptions[0]
        asr_confidence = top_transcription.get("transcriptionConfidence", 0)

        if asr_confidence < 0.6:
            return elicit_slot(
                event,
                "OrderId",
                "聞き取りにくかったため、もう一度注文番号をお教えください。",
            )

    # スロット値のバリデーション（order_lookup.py と同様）
    slots = event["sessionState"]["intent"]["slots"]
    order_id_slot = slots.get("OrderId")

    if order_id_slot and order_id_slot.get("value"):
        order_id = order_id_slot["value"]["interpretedValue"]
        if not order_id.startswith("ORD-"):
            return elicit_slot(
                event,
                "OrderId",
                "注文番号はORD-で始まる形式です（例：ORD-001）。もう一度お教えください。",
            )

    return delegate(event)


def handle_fulfillment(event):
    """フルフィルメントコードフック（簡易版）。"""
    slots = event["sessionState"]["intent"]["slots"]
    order_id = slots["OrderId"]["value"]["interpretedValue"]
    message = f"注文番号 {order_id} の確認を承りました。担当部署にお繋ぎいたします。"
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
