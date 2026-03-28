# =============================================================================
# Amazon SageMaker #8 — シリーズ全体のリソース一括クリーンアップ
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #8】SageMaker AIとBedrockを連携させて実践活用
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
SageMaker シリーズ（#1〜#8）全体で作成したリソースを一括削除する。
課金の継続を防ぐため、ハンズオン終了後に必ず実行すること。
"""

import boto3

sm_client = boto3.client("sagemaker")
s3_client = boto3.client("s3")

# ---------------------------------------------------------------------------
# 1. エンドポイントの削除
# ---------------------------------------------------------------------------

print("=" * 50)
print("1. エンドポイントの削除")
print("=" * 50)

endpoints_to_delete = [
    "xgboost-income-realtime",
    "xgboost-income-serverless",
]

# JumpStart エンドポイント（動的名称のため一覧から検索）
response = sm_client.list_endpoints(
    SortBy="CreationTime",
    SortOrder="Descending",
    MaxResults=20,
)
for ep in response["Endpoints"]:
    if any(
        keyword in ep["EndpointName"].lower()
        for keyword in ["llama", "jumpstart", "distilbert", "huggingface"]
    ):
        endpoints_to_delete.append(ep["EndpointName"])

for endpoint_name in endpoints_to_delete:
    try:
        sm_client.delete_endpoint(EndpointName=endpoint_name)
        print(f"  削除: {endpoint_name}")
    except sm_client.exceptions.ClientError as e:
        if "Could not find" in str(e):
            print(f"  スキップ（存在しない）: {endpoint_name}")
        else:
            print(f"  エラー: {endpoint_name} - {e}")

# ---------------------------------------------------------------------------
# 2. エンドポイント設定の削除
# ---------------------------------------------------------------------------

print(f"\n{'='*50}")
print("2. エンドポイント設定の削除")
print("=" * 50)

for endpoint_name in endpoints_to_delete:
    try:
        sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
        print(f"  削除: {endpoint_name}")
    except sm_client.exceptions.ClientError:
        pass  # エンドポイント削除時に自動削除される場合がある

# ---------------------------------------------------------------------------
# 3. モデルの削除
# ---------------------------------------------------------------------------

print(f"\n{'='*50}")
print("3. モデルの削除")
print("=" * 50)

response = sm_client.list_models(
    SortBy="CreationTime",
    SortOrder="Descending",
    MaxResults=20,
)
for model in response["Models"]:
    if any(
        keyword in model["ModelName"].lower()
        for keyword in ["xgboost", "income", "jumpstart", "llama", "distilbert"]
    ):
        try:
            sm_client.delete_model(ModelName=model["ModelName"])
            print(f"  削除: {model['ModelName']}")
        except Exception as e:
            print(f"  エラー: {model['ModelName']} - {e}")

# ---------------------------------------------------------------------------
# 4. パイプラインの削除
# ---------------------------------------------------------------------------

print(f"\n{'='*50}")
print("4. パイプラインの削除")
print("=" * 50)

pipelines_to_delete = [
    "income-prediction-pipeline",
    "bedrock-review-analysis-pipeline",
]
for pipeline_name in pipelines_to_delete:
    try:
        sm_client.delete_pipeline(PipelineName=pipeline_name)
        print(f"  削除: {pipeline_name}")
    except sm_client.exceptions.ClientError as e:
        if "Could not find" in str(e) or "does not exist" in str(e):
            print(f"  スキップ（存在しない）: {pipeline_name}")
        else:
            print(f"  エラー: {pipeline_name} - {e}")

# ---------------------------------------------------------------------------
# 5. S3 データの削除
# ---------------------------------------------------------------------------

print(f"\n{'='*50}")
print("5. S3データの削除")
print("=" * 50)

import sagemaker

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"

paginator = s3_client.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

delete_count = 0
for page in pages:
    if "Contents" in page:
        objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
        s3_client.delete_objects(Bucket=bucket, Delete={"Objects": objects})
        delete_count += len(objects)

print(f"  S3オブジェクト {delete_count}件を削除しました")
print(f"  バケット: s3://{bucket}/{prefix}/")

# ---------------------------------------------------------------------------
# 完了
# ---------------------------------------------------------------------------

print(f"\n{'='*50}")
print("クリーンアップ完了！")
print("=" * 50)
print("注意: SageMaker Studio 自体も使わない場合は、")
print("      Studio のドメインとユーザーも削除してください。")
