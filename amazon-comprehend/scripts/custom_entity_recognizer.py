# Amazon Comprehend #3 — カスタムエンティティレコグナイザーのトレーニング
# ファイル: custom_entity_recognizer.py
# 概要: エンティティリスト方式でカスタムエンティティレコグナイザーをトレーニングし、
#       ORDER_ID / POLICY_ID / CUSTOMER_NAME といったドメイン固有のエンティティを抽出する。

import boto3

comprehend = boto3.client("comprehend", region_name="ap-northeast-1")


def create_entity_recognizer(
    recognizer_name,
    entity_types,
    s3_entity_list_uri,
    s3_documents_uri,
    data_access_role_arn,
    language_code="ja",
):
    """カスタムエンティティレコグナイザーをトレーニングする。

    Parameters
    ----------
    recognizer_name : str
        レコグナイザーの名前
    entity_types : list[dict]
        エンティティタイプのリスト（例: [{"Type": "ORDER_ID"}, ...]）
    s3_entity_list_uri : str
        エンティティリスト CSV の S3 URI
    s3_documents_uri : str
        トレーニング用ドキュメントの S3 URI
    data_access_role_arn : str
        S3 アクセス用 IAM ロールの ARN
    language_code : str
        言語コード

    Returns
    -------
    str
        レコグナイザーの ARN
    """
    response = comprehend.create_entity_recognizer(
        RecognizerName=recognizer_name,
        LanguageCode=language_code,
        InputDataConfig={
            "EntityTypes": entity_types,
            "EntityList": {
                "S3Uri": s3_entity_list_uri,
            },
            "Documents": {
                "S3Uri": s3_documents_uri,
            },
            "DataFormat": "COMPREHEND_CSV",
        },
        DataAccessRoleArn=data_access_role_arn,
    )

    recognizer_arn = response["EntityRecognizerArn"]
    print(f"レコグナイザーARN: {recognizer_arn}")
    return recognizer_arn


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    arn = create_entity_recognizer(
        recognizer_name="order-entity-recognizer",
        entity_types=[
            {"Type": "ORDER_ID"},
            {"Type": "POLICY_ID"},
            {"Type": "CUSTOMER_NAME"},
        ],
        s3_entity_list_uri="s3://my-comprehend-bucket/training/entity/entity_list.csv",
        s3_documents_uri="s3://my-comprehend-bucket/training/entity/documents/",
        data_access_role_arn="arn:aws:iam::123456789012:role/ComprehendDataAccessRole",
    )
