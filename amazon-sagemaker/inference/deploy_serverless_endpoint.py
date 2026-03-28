# =============================================================================
# Amazon SageMaker #5 — サーバーレスエンドポイントのデプロイ
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #5】4つの推論方式を比較しながらモデルをデプロイ
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
Serverless Inference でモデルをデプロイし、コールドスタートの影響を計測する。
"""

import time
import sagemaker
import boto3
from sagemaker.serverless import ServerlessInferenceConfig

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
role = sagemaker.get_execution_role()
sm_client = boto3.client("sagemaker")
runtime_client = boto3.client("sagemaker-runtime")

# トレーニング済みモデルの情報を取得
response = sm_client.list_training_jobs(
    NameContains="xgboost-income",
    MaxResults=1,
    SortBy="CreationTime",
    SortOrder="Descending",
)
latest_job = response["TrainingJobSummaries"][0]
job_info = sm_client.describe_training_job(TrainingJobName=latest_job["TrainingJobName"])
model_data = job_info["ModelArtifacts"]["S3ModelArtifacts"]

xgboost_image = sagemaker.image_uris.retrieve(
    framework="xgboost",
    region=session.boto_region_name,
    version="1.7-1",
)

# ---------------------------------------------------------------------------
# 2. サーバーレスエンドポイントの作成
# ---------------------------------------------------------------------------

serverless_config = ServerlessInferenceConfig(
    memory_size_in_mb=2048,     # メモリ: 2048 MB
    max_concurrency=5,          # 最大同時実行数
)

model = sagemaker.Model(
    image_uri=xgboost_image,
    model_data=model_data,
    role=role,
    sagemaker_session=session,
)

endpoint_name = "xgboost-income-serverless"
print(f"サーバーレスエンドポイント '{endpoint_name}' のデプロイ開始...")

predictor = model.deploy(
    serverless_inference_config=serverless_config,
    endpoint_name=endpoint_name,
)

print("デプロイ完了！")

# ---------------------------------------------------------------------------
# 3. コールドスタート計測
# ---------------------------------------------------------------------------

test_data = "0.5,0.3,0.8,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0"

# 1回目（コールドスタート）
start = time.time()
response = runtime_client.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="text/csv",
    Body=test_data,
)
cold_start_time = time.time() - start
result = response["Body"].read().decode("utf-8")
print(f"\nコールドスタート: {cold_start_time:.2f}秒 (結果: {result.strip()})")

# 2回目（ウォームスタート）
start = time.time()
response = runtime_client.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="text/csv",
    Body=test_data,
)
warm_start_time = time.time() - start
result = response["Body"].read().decode("utf-8")
print(f"ウォームスタート: {warm_start_time:.2f}秒 (結果: {result.strip()})")

print(f"\nコールドスタートの影響: {cold_start_time / warm_start_time:.1f}倍")
