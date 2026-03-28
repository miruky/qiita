# Amazon Comprehend #2 — バッチ処理と非同期ジョブ
# ファイル: batch_and_async.py
# 概要: 複数テキストの一括分析（BatchDetectSentiment）と
#       S3 上の大規模データを対象にした非同期ジョブの実行例。

import time

import boto3

# Comprehendクライアントの作成
comprehend = boto3.client("comprehend", region_name="ap-northeast-1")


# ---------------------------------------------------------------------------
# バッチ処理（最大25件のテキストを1回のAPI呼び出しで分析）
# ---------------------------------------------------------------------------


def batch_sentiment_analysis(texts, language_code="ja"):
    """複数テキストの感情を一括分析する。

    Parameters
    ----------
    texts : list[str]
        分析対象のテキストリスト（最大25件）
    language_code : str
        言語コード（デフォルト: ja）

    Returns
    -------
    dict
        Comprehend BatchDetectSentiment レスポンス
    """
    response = comprehend.batch_detect_sentiment(
        TextList=texts,
        LanguageCode=language_code,
    )

    print("■ バッチ感情分析結果:")
    for result in response["ResultList"]:
        idx = result["Index"]
        print(f"  [{idx}] {texts[idx][:30]}...")
        print(f"       感情: {result['Sentiment']}")
    print()

    # エラーがあれば表示
    if response["ErrorList"]:
        print("■ エラー:")
        for error in response["ErrorList"]:
            print(f"  [{error['Index']}] {error['ErrorCode']}: {error['ErrorMessage']}")

    return response


# ---------------------------------------------------------------------------
# 非同期ジョブ（S3 上の大規模データを分析）
# ---------------------------------------------------------------------------


def start_sentiment_job(input_s3_uri, output_s3_uri, data_access_role_arn):
    """感情分析の非同期ジョブを開始する。

    Parameters
    ----------
    input_s3_uri : str
        入力ドキュメントの S3 URI
    output_s3_uri : str
        出力先の S3 URI
    data_access_role_arn : str
        S3 アクセス用 IAM ロールの ARN

    Returns
    -------
    str
        ジョブID
    """
    response = comprehend.start_sentiment_detection_job(
        InputDataConfig={
            "S3Uri": input_s3_uri,
            "InputFormat": "ONE_DOC_PER_LINE",  # 1行1ドキュメント
        },
        OutputDataConfig={
            "S3Uri": output_s3_uri,
        },
        DataAccessRoleArn=data_access_role_arn,
        LanguageCode="ja",
        JobName="customer-review-sentiment-analysis",
    )

    job_id = response["JobId"]
    print(f"ジョブ開始: {job_id}")
    return job_id


def wait_for_job(job_id):
    """ジョブの完了を待機する。

    Parameters
    ----------
    job_id : str
        ジョブID

    Returns
    -------
    dict
        ジョブプロパティ
    """
    while True:
        response = comprehend.describe_sentiment_detection_job(
            JobId=job_id
        )
        status = response["SentimentDetectionJobProperties"]["JobStatus"]
        print(f"ステータス: {status}")

        if status in ("COMPLETED", "FAILED", "STOP_REQUESTED", "STOPPED"):
            return response["SentimentDetectionJobProperties"]

        time.sleep(30)  # 30秒ごとにポーリング


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # バッチ感情分析
    reviews = [
        "とても良い商品です。また購入したいです。",
        "期待していたほどではなかった。値段の割に品質がイマイチ。",
        "普通ですね。可もなく不可もなく。",
        "最悪です。すぐに壊れました。返品します。",
        "デザインは好きだけど、機能がいまいち。総合的にはまあまあ。",
    ]
    batch_sentiment_analysis(reviews)

    # 非同期ジョブの例（実行するにはS3バケットとIAMロールが必要）
    # job_id = start_sentiment_job(
    #     input_s3_uri="s3://my-comprehend-bucket/input/reviews.txt",
    #     output_s3_uri="s3://my-comprehend-bucket/output/",
    #     data_access_role_arn="arn:aws:iam::123456789012:role/ComprehendDataAccessRole",
    # )
    # result = wait_for_job(job_id)
    # print(result)
