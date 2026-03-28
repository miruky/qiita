# Amazon Comprehend #3 — モデルのデプロイと推論
# ファイル: model_deploy_and_inference.py
# 概要: カスタム分類子のリアルタイム推論エンドポイントを作成し、
#       ドキュメント分類と非同期バッチ分類を実行する。
#       使用後はエンドポイントを削除してコストを抑える。

import boto3

comprehend = boto3.client("comprehend", region_name="ap-northeast-1")


def create_endpoint(endpoint_name, model_arn, inference_units=1):
    """カスタムモデルのリアルタイム推論エンドポイントを作成する。

    Parameters
    ----------
    endpoint_name : str
        エンドポイント名
    model_arn : str
        トレーニング済みモデルの ARN
    inference_units : int
        推論ユニット数（1 IU = 100文字/秒）

    Returns
    -------
    str
        エンドポイントの ARN
    """
    response = comprehend.create_endpoint(
        EndpointName=endpoint_name,
        ModelArn=model_arn,
        DesiredInferenceUnits=inference_units,
    )

    endpoint_arn = response["EndpointArn"]
    print(f"エンドポイントARN: {endpoint_arn}")
    return endpoint_arn


def classify_document(text, endpoint_arn):
    """カスタム分類子でドキュメントを分類する。

    Parameters
    ----------
    text : str
        分類対象のテキスト
    endpoint_arn : str
        エンドポイントの ARN

    Returns
    -------
    dict
        ClassifyDocument レスポンス
    """
    response = comprehend.classify_document(
        Text=text,
        EndpointArn=endpoint_arn,
    )

    print(f"テキスト: {text[:50]}...")
    print("分類結果:")
    for label in response["Classes"]:
        print(f"  {label['Name']}: {label['Score']:.4f}")
    print()

    return response


def start_batch_classification(
    classifier_arn, input_s3_uri, output_s3_uri, data_access_role_arn
):
    """非同期バッチ分類ジョブを実行する。

    Parameters
    ----------
    classifier_arn : str
        分類子の ARN
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
    response = comprehend.start_document_classification_job(
        JobName="batch-classification-job",
        DocumentClassifierArn=classifier_arn,
        InputDataConfig={
            "S3Uri": input_s3_uri,
            "InputFormat": "ONE_DOC_PER_LINE",
        },
        OutputDataConfig={
            "S3Uri": output_s3_uri,
        },
        DataAccessRoleArn=data_access_role_arn,
    )

    job_id = response["JobId"]
    print(f"ジョブID: {job_id}")
    return job_id


def delete_endpoint(endpoint_arn):
    """エンドポイントを削除する。

    エンドポイントは起動中は常に課金されるため、
    使用後は必ず削除してください。
    """
    comprehend.delete_endpoint(EndpointArn=endpoint_arn)
    print("エンドポイントを削除しました")


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 以下の値を自分の環境に合わせて変更してください
    CLASSIFIER_ARN = "arn:aws:comprehend:ap-northeast-1:123456789012:document-classifier/customer-support-classifier"

    # エンドポイント作成
    ep_arn = create_endpoint("support-classifier-endpoint", CLASSIFIER_ARN)

    # 分類テスト
    classify_document(
        "ログインできなくなりました。パスワードをリセットしたいです。",
        ep_arn,
    )
    classify_document(
        "先日注文した商品を返品したいのですが、手続きを教えてください。",
        ep_arn,
    )

    # テスト後はエンドポイントを削除（コスト節約）
    # delete_endpoint(ep_arn)
