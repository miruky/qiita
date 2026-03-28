# Amazon Comprehend #3 — カスタム分類子のトレーニング
# ファイル: custom_classifier.py
# 概要: 独自カテゴリ（ACCOUNT_QUESTION / TICKET_REFUND / COMPLAINT）で
#       ドキュメントを自動分類するカスタムモデルをトレーニングする。

import boto3

comprehend = boto3.client("comprehend", region_name="ap-northeast-1")


def create_classifier(
    classifier_name,
    s3_training_uri,
    s3_output_uri,
    data_access_role_arn,
    language_code="ja",
    mode="MULTI_CLASS",
):
    """カスタム分類子をトレーニングする。

    Parameters
    ----------
    classifier_name : str
        分類子の名前
    s3_training_uri : str
        トレーニングデータ CSV の S3 URI
    s3_output_uri : str
        出力先の S3 URI
    data_access_role_arn : str
        S3 アクセス用 IAM ロールの ARN
    language_code : str
        言語コード
    mode : str
        分類モード（MULTI_CLASS / MULTI_LABEL）

    Returns
    -------
    str
        分類子の ARN
    """
    response = comprehend.create_document_classifier(
        DocumentClassifierName=classifier_name,
        LanguageCode=language_code,
        Mode=mode,
        InputDataConfig={
            "S3Uri": s3_training_uri,
            "DataFormat": "COMPREHEND_CSV",
        },
        OutputDataConfig={
            "S3Uri": s3_output_uri,
        },
        DataAccessRoleArn=data_access_role_arn,
    )

    classifier_arn = response["DocumentClassifierArn"]
    print(f"分類子ARN: {classifier_arn}")
    return classifier_arn


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 以下の値を自分の環境に合わせて変更してください
    arn = create_classifier(
        classifier_name="customer-support-classifier",
        s3_training_uri="s3://my-comprehend-bucket/training/classification/training_data.csv",
        s3_output_uri="s3://my-comprehend-bucket/output/classification/",
        data_access_role_arn="arn:aws:iam::123456789012:role/ComprehendDataAccessRole",
    )
