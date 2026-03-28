# Amazon Comprehend #5 — 会話ログ分析とコンテキストスコアリング
# ファイル: conversation_analyzer.py
# 概要: 生成 AI アプリケーションの品質改善のために、
#       会話ログの感情分析・キーフレーズ抽出と
#       RAG のコンテキスト関連性スコアリングを行う。

import boto3

comprehend = boto3.client("comprehend", region_name="ap-northeast-1")


def analyze_conversation_log(conversations):
    """会話ログを分析してインサイトを抽出する。

    Parameters
    ----------
    conversations : list[dict]
        会話ログのリスト。各要素は {"user_input": str, "timestamp": str} の形式。

    Returns
    -------
    dict
        分析結果（感情分布、キートピック、ネガティブ会話リスト）
    """
    results = {
        "total": len(conversations),
        "sentiment_distribution": {
            "POSITIVE": 0,
            "NEGATIVE": 0,
            "NEUTRAL": 0,
            "MIXED": 0,
        },
        "key_topics": [],
        "negative_conversations": [],
    }

    all_texts = []

    for conv in conversations:
        user_input = conv["user_input"]
        all_texts.append(user_input)

        # 感情分析
        sentiment = comprehend.detect_sentiment(
            Text=user_input[:5000],
            LanguageCode="ja",
        )

        results["sentiment_distribution"][sentiment["Sentiment"]] += 1

        # ネガティブな会話を記録
        if sentiment["Sentiment"] == "NEGATIVE":
            results["negative_conversations"].append(
                {
                    "input": user_input[:100],
                    "score": sentiment["SentimentScore"]["Negative"],
                    "timestamp": conv.get("timestamp", ""),
                }
            )

    # キーフレーズ抽出（バッチ API の 25 件上限に合わせる）
    for text in all_texts[:25]:
        phrases = comprehend.detect_key_phrases(
            Text=text[:5000],
            LanguageCode="ja",
        )
        for kp in phrases["KeyPhrases"]:
            if kp["Score"] > 0.9:
                results["key_topics"].append(kp["Text"])

    return results


def score_context_relevance(query, contexts, language_code="ja"):
    """コンテキストの関連性を感情分析でスコアリングする。

    RAG で取得されたドキュメントの感情を分析し、
    エンティティ数と合わせて関連性の指標を返す。

    Parameters
    ----------
    query : str
        ユーザーの質問テキスト
    contexts : list[dict]
        コンテキストのリスト。各要素は {"text": str, "score": float} の形式。
    language_code : str
        言語コード

    Returns
    -------
    list[dict]
        スコアリング済みコンテキストのリスト
    """
    # クエリの感情を分析
    comprehend.detect_sentiment(
        Text=query,
        LanguageCode=language_code,
    )

    scored_contexts = []
    for ctx in contexts:
        # コンテキストの感情を分析
        ctx_sentiment = comprehend.detect_sentiment(
            Text=ctx["text"][:5000],
            LanguageCode=language_code,
        )

        # エンティティの関連性もチェック
        ctx_entities = comprehend.detect_entities(
            Text=ctx["text"][:5000],
            LanguageCode=language_code,
        )

        entity_count = len(ctx_entities["Entities"])

        scored_contexts.append(
            {
                "text": ctx["text"],
                "sentiment": ctx_sentiment["Sentiment"],
                "entity_count": entity_count,
                "original_score": ctx.get("score", 0),
            }
        )

    return scored_contexts


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 会話ログ分析のサンプル
    sample_conversations = [
        {"user_input": "注文した商品がまだ届きません", "timestamp": "2026-03-01T10:00:00"},
        {"user_input": "素晴らしいサービスでした", "timestamp": "2026-03-01T10:05:00"},
        {"user_input": "返品の手続きを教えてください", "timestamp": "2026-03-01T10:10:00"},
    ]
    result = analyze_conversation_log(sample_conversations)
    print(f"感情分布: {result['sentiment_distribution']}")
    print(f"キートピック: {result['key_topics']}")
    print(f"ネガティブ会話数: {len(result['negative_conversations'])}")
