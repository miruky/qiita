# =============================================================================
# Amazon SageMaker #5 — バッチ変換による一括推論
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #5】4つの推論方式を比較しながらモデルをデプロイ
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
SageMaker Batch Transform でテストデータを一括推論する。
エンドポイント不要・大量データ向けの推論方式。
"""

import pandas as pd
import sagemaker
import boto3

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
role = sagemaker.get_execution_role()
sm_client = boto3.client("sagemaker")

# モデルアーティファクト取得
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
# 2. バッチ変換用のテストデータを準備
# ---------------------------------------------------------------------------

test_df = pd.read_csv(f"s3://{bucket}/{prefix}/processing/output/test.csv")
target_col = "income"
feature_cols = [c for c in test_df.columns if c != target_col]

# 目的変数なしの特徴量のみCSV
test_features = test_df[feature_cols]
batch_input_path = f"s3://{bucket}/{prefix}/batch/input/test_features.csv"
test_features.to_csv(batch_input_path, index=False, header=False)
print(f"バッチ入力データ: {batch_input_path}")

# ---------------------------------------------------------------------------
# 3. Transformer の設定と実行
# ---------------------------------------------------------------------------

model = sagemaker.Model(
    image_uri=xgboost_image,
    model_data=model_data,
    role=role,
    sagemaker_session=session,
)

transformer = model.transformer(
    instance_count=1,
    instance_type="ml.m5.large",
    output_path=f"s3://{bucket}/{prefix}/batch/output",
    accept="text/csv",
    assemble_with="Line",
    strategy="MultiRecord",
    max_payload=6,  # MB
)

print("バッチ変換ジョブ開始...")

transformer.transform(
    data=batch_input_path,
    content_type="text/csv",
    split_type="Line",
)

transformer.wait()
print("バッチ変換完了！")

# ---------------------------------------------------------------------------
# 4. 結果の確認
# ---------------------------------------------------------------------------

import io

s3_client = boto3.client("s3")
output_key = f"{prefix}/batch/output/test_features.csv.out"

response = s3_client.get_object(Bucket=bucket, Key=output_key)
predictions = response["Body"].read().decode("utf-8").strip().split("\n")
predictions = [float(p) for p in predictions]

print(f"\n推論件数: {len(predictions)}")
print(f"高所得（>0.5）: {sum(1 for p in predictions if p >= 0.5)}件")
print(f"低所得（≤0.5）: {sum(1 for p in predictions if p < 0.5)}件")
