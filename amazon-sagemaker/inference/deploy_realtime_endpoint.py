# =============================================================================
# Amazon SageMaker #5 — リアルタイム推論エンドポイントのデプロイと推論
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #5】4つの推論方式を比較しながらモデルをデプロイ
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: train_xgboost.py でトレーニング済みモデルが S3 に存在すること
# =============================================================================

"""
トレーニング済み XGBoost モデルからリアルタイムエンドポイントを作成し、
テストデータで推論を実行する。
"""

import time
import pandas as pd
import numpy as np
import sagemaker
import boto3
from sagemaker.model import Model

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
role = sagemaker.get_execution_role()
sm_client = boto3.client("sagemaker")
runtime_client = boto3.client("sagemaker-runtime")

# 最新のトレーニングジョブからモデルを取得
response = sm_client.list_training_jobs(
    NameContains="xgboost-income",
    MaxResults=1,
    SortBy="CreationTime",
    SortOrder="Descending",
)
latest_job = response["TrainingJobSummaries"][0]
job_info = sm_client.describe_training_job(TrainingJobName=latest_job["TrainingJobName"])
model_data = job_info["ModelArtifacts"]["S3ModelArtifacts"]

print(f"トレーニングジョブ: {latest_job['TrainingJobName']}")
print(f"モデルアーティファクト: {model_data}")

# ---------------------------------------------------------------------------
# 2. SageMaker Model の作成
# ---------------------------------------------------------------------------

xgboost_image = sagemaker.image_uris.retrieve(
    framework="xgboost",
    region=session.boto_region_name,
    version="1.7-1",
)

model = Model(
    image_uri=xgboost_image,
    model_data=model_data,
    role=role,
    sagemaker_session=session,
    name="xgboost-income-model",
)
print(f"モデル名: {model.name}")

# ---------------------------------------------------------------------------
# 3. リアルタイムエンドポイントのデプロイ
# ---------------------------------------------------------------------------

endpoint_name = "xgboost-income-realtime"
print(f"\nエンドポイント '{endpoint_name}' のデプロイ開始...")
start_time = time.time()

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name=endpoint_name,
)

deploy_time = time.time() - start_time
print(f"デプロイ完了！ （所要時間: {deploy_time:.0f}秒）")

# ---------------------------------------------------------------------------
# 4. テストデータで推論
# ---------------------------------------------------------------------------

test_df = pd.read_csv(f"s3://{bucket}/{prefix}/processing/output/test.csv")
target_col = "income"

# 特徴量のみ取得（目的変数を除外）
feature_cols = [c for c in test_df.columns if c != target_col]
test_features = test_df[feature_cols]
test_labels = test_df[target_col]

# CSV 文字列に変換して推論リクエスト
sample = test_features.head(5)
csv_payload = sample.to_csv(index=False, header=False)

response = runtime_client.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="text/csv",
    Body=csv_payload,
)

predictions = response["Body"].read().decode("utf-8").strip().split("\n")
predictions = [float(p) for p in predictions]

print("\n推論結果（最初の5件）:")
for i, (pred, actual) in enumerate(zip(predictions, test_labels.head(5))):
    label = "高所得" if pred >= 0.5 else "低所得"
    actual_label = "高所得" if actual == 1 else "低所得"
    print(f"  サンプル{i+1}: 予測={pred:.4f}({label}) / 実際={actual_label}")

# ---------------------------------------------------------------------------
# 5. バッチ推論 & AUC 評価
# ---------------------------------------------------------------------------

# 全テストデータで推論
all_csv = test_features.to_csv(index=False, header=False)
response = runtime_client.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="text/csv",
    Body=all_csv,
)
all_predictions = [
    float(p) for p in response["Body"].read().decode("utf-8").strip().split("\n")
]

# 精度評価
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

pred_labels = [1 if p >= 0.5 else 0 for p in all_predictions]

print("\nモデル評価結果:")
print(f"  Accuracy:  {accuracy_score(test_labels, pred_labels):.4f}")
print(f"  Precision: {precision_score(test_labels, pred_labels):.4f}")
print(f"  Recall:    {recall_score(test_labels, pred_labels):.4f}")
print(f"  F1 Score:  {f1_score(test_labels, pred_labels):.4f}")
print(f"  AUC:       {roc_auc_score(test_labels, all_predictions):.4f}")
