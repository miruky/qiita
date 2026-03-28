# Amazon Comprehend #2 — テキスト分析の基本（単体 API）
# ファイル: text_analysis_basics.py
# 概要: boto3 を使った Comprehend 組み込み NLP API の基本操作。
#       感情分析・エンティティ認識・キーフレーズ抽出・構文解析・総合分析を行う。

import boto3

# Comprehendクライアントの作成
comprehend = boto3.client("comprehend", region_name="ap-northeast-1")


def analyze_sentiment(text, language_code="ja"):
    """テキストの感情を分析する。

    Parameters
    ----------
    text : str
        分析対象のテキスト
    language_code : str
        言語コード（デフォルト: ja）

    Returns
    -------
    dict
        Comprehend DetectSentiment レスポンス
    """
    response = comprehend.detect_sentiment(
        Text=text,
        LanguageCode=language_code,
    )

    print(f"テキスト: {text}")
    print(f"感情: {response['Sentiment']}")
    print("スコア:")
    for sentiment, score in response["SentimentScore"].items():
        print(f"  {sentiment}: {score:.4f}")
    print()

    return response


def detect_entities(text, language_code="ja"):
    """テキストからエンティティを抽出する。

    Parameters
    ----------
    text : str
        分析対象のテキスト
    language_code : str
        言語コード（デフォルト: ja）

    Returns
    -------
    dict
        Comprehend DetectEntities レスポンス
    """
    response = comprehend.detect_entities(
        Text=text,
        LanguageCode=language_code,
    )

    print(f"テキスト: {text}")
    print("検出されたエンティティ:")
    for entity in response["Entities"]:
        print(f"  [{entity['Type']}] {entity['Text']} (スコア: {entity['Score']:.4f})")
    print()

    return response


def detect_key_phrases(text, language_code="ja"):
    """テキストからキーフレーズを抽出する。

    Parameters
    ----------
    text : str
        分析対象のテキスト
    language_code : str
        言語コード（デフォルト: ja）

    Returns
    -------
    dict
        Comprehend DetectKeyPhrases レスポンス
    """
    response = comprehend.detect_key_phrases(
        Text=text,
        LanguageCode=language_code,
    )

    print(f"テキスト: {text}")
    print("キーフレーズ:")
    for phrase in response["KeyPhrases"]:
        print(f"  「{phrase['Text']}」 (スコア: {phrase['Score']:.4f})")
    print()

    return response


def detect_syntax(text, language_code="ja"):
    """テキストの構文を解析する。

    Parameters
    ----------
    text : str
        分析対象のテキスト
    language_code : str
        言語コード（デフォルト: ja）

    Returns
    -------
    dict
        Comprehend DetectSyntax レスポンス
    """
    response = comprehend.detect_syntax(
        Text=text,
        LanguageCode=language_code,
    )

    print(f"テキスト: {text}")
    print("構文解析結果:")
    for token in response["SyntaxTokens"]:
        pos = token["PartOfSpeech"]
        print(f"  {token['Text']:12s} → {pos['Tag']:10s} (スコア: {pos['Score']:.4f})")
    print()

    return response


def comprehensive_analysis(text, language_code="ja"):
    """テキストの総合分析を実行する。

    感情分析・エンティティ認識・キーフレーズ抽出をまとめて実行し
    結果を辞書で返す。

    Parameters
    ----------
    text : str
        分析対象のテキスト
    language_code : str
        言語コード（デフォルト: ja）

    Returns
    -------
    dict
        各分析結果をまとめた辞書
    """
    print("=" * 60)
    print(f"【総合分析】{text[:50]}...")
    print("=" * 60)

    # 1. 感情分析
    sentiment = comprehend.detect_sentiment(
        Text=text, LanguageCode=language_code
    )
    print(f"\n■ 感情: {sentiment['Sentiment']}")

    # 2. エンティティ認識
    entities = comprehend.detect_entities(
        Text=text, LanguageCode=language_code
    )
    if entities["Entities"]:
        print("\n■ エンティティ:")
        for e in entities["Entities"]:
            print(f"  [{e['Type']}] {e['Text']}")

    # 3. キーフレーズ抽出
    key_phrases = comprehend.detect_key_phrases(
        Text=text, LanguageCode=language_code
    )
    if key_phrases["KeyPhrases"]:
        print("\n■ キーフレーズ:")
        for kp in key_phrases["KeyPhrases"]:
            print(f"  「{kp['Text']}」")

    print()
    return {
        "sentiment": sentiment,
        "entities": entities,
        "key_phrases": key_phrases,
    }


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 感情分析
    analyze_sentiment("この商品はとても使いやすく、デザインも気に入っています。")
    analyze_sentiment("配送が遅すぎて困りました。二度と利用しません。")
    analyze_sentiment("普通でした。特に良くも悪くもないです。")

    # エンティティ認識
    detect_entities(
        "田中太郎は2026年3月にAWSの東京リージョンでComprehendを使い始めました。"
    )

    # キーフレーズ抽出
    detect_key_phrases(
        "Amazon Comprehendは自然言語処理サービスで、テキストから重要な情報を自動的に抽出できます。"
    )

    # 構文解析
    detect_syntax("Amazon Comprehendは素晴らしいサービスです。")

    # 総合分析
    review = (
        "先週AmazonでKindle Paperwhiteを購入しました。"
        "画面が見やすく、バッテリーも長持ちで大満足です。"
        "ただし、カバーが別売りなのは少し残念でした。"
    )
    comprehensive_analysis(review)
