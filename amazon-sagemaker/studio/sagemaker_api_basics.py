# =============================================================================
# Amazon SageMaker #2 — SageMaker SDK / boto3 の基本操作
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #2】SageMaker Studioを立ち上げてはじめての
#              ノートブックを動かしてみる
#
# 実行環境: SageMaker Studio JupyterLab（ml.t3.medium 推奨 — 無料利用枠対象）
# =============================================================================

"""
SageMaker Studio 上で動作確認するための基礎スクリプト。
環境情報の確認、SageMaker API の基本操作、S3 操作、JumpStart モデル一覧を行う。
"""

import sys
import json
import boto3
import sagemaker
from sagemaker import get_execution_role

# ---------------------------------------------------------------------------
# 1. 環境の確認
# ---------------------------------------------------------------------------

print(f"Python version: {sys.version}")
print(f"SageMaker SDK version: {sagemaker.__version__}")
print(f"Boto3 version: {boto3.__version__}")

# ---------------------------------------------------------------------------
# 2. SageMaker セッション情報
# ---------------------------------------------------------------------------

session = sagemaker.Session()
region = session.boto_region_name
role = get_execution_role()
default_bucket = session.default_bucket()

print(f"\nリージョン: {region}")
print(f"実行ロール: {role}")
print(f"デフォルトS3バケット: {default_bucket}")

# ---------------------------------------------------------------------------
# 3. トレーニングジョブの一覧を取得
# ---------------------------------------------------------------------------

sm_client = boto3.client("sagemaker")

response = sm_client.list_training_jobs(
    MaxResults=10,
    SortBy="CreationTime",
    SortOrder="Descending",
)

if response["TrainingJobSummaries"]:
    for job in response["TrainingJobSummaries"]:
        print(f"ジョブ名: {job['TrainingJobName']}")
        print(f"ステータス: {job['TrainingJobStatus']}")
        print(f"作成日時: {job['CreationTime']}")
        print("---")
else:
    print("トレーニングジョブはまだありません。")
    print("次回以降のハンズオンで作成していきます！")

# ---------------------------------------------------------------------------
# 4. トレーニング向け主要インスタンスタイプ一覧
# ---------------------------------------------------------------------------

training_instances = {
    "ml.m5.large": {"vCPU": 2, "Memory": "8 GB", "GPU": "なし", "用途": "小規模トレーニング"},
    "ml.m5.xlarge": {"vCPU": 4, "Memory": "16 GB", "GPU": "なし", "用途": "中規模トレーニング"},
    "ml.c5.xlarge": {"vCPU": 4, "Memory": "8 GB", "GPU": "なし", "用途": "CPU重視の計算"},
    "ml.p3.2xlarge": {"vCPU": 8, "Memory": "61 GB", "GPU": "V100 x1", "用途": "深層学習"},
    "ml.g4dn.xlarge": {"vCPU": 4, "Memory": "16 GB", "GPU": "T4 x1", "用途": "コスパ重視の深層学習"},
    "ml.g5.xlarge": {"vCPU": 4, "Memory": "16 GB", "GPU": "A10G x1", "用途": "最新GPU深層学習"},
}

print(f"\n{'インスタンス':<18} {'vCPU':>5} {'メモリ':>8} {'GPU':>10} {'用途'}")
print("-" * 70)
for instance, spec in training_instances.items():
    print(f"{instance:<18} {spec['vCPU']:>5} {spec['Memory']:>8} {spec['GPU']:>10} {spec['用途']}")

# ---------------------------------------------------------------------------
# 5. S3 バケットの操作
# ---------------------------------------------------------------------------

bucket = session.default_bucket()
prefix = "sagemaker-handson"

test_data = {
    "message": "SageMaker AIハンズオンのテストデータです",
    "series": "Amazon SageMaker #2",
    "author": "miruky",
}

s3_client = boto3.client("s3")
s3_client.put_object(
    Bucket=bucket,
    Key=f"{prefix}/test_data.json",
    Body=json.dumps(test_data, ensure_ascii=False),
    ContentType="application/json",
)
print(f"\nテストデータをアップロードしました: s3://{bucket}/{prefix}/test_data.json")

# アップロードしたデータを確認
response = s3_client.get_object(Bucket=bucket, Key=f"{prefix}/test_data.json")
content = json.loads(response["Body"].read().decode("utf-8"))
print("取得したデータ:")
for key, value in content.items():
    print(f"  {key}: {value}")

# ---------------------------------------------------------------------------
# 6. JumpStart で利用可能なモデルを確認
# ---------------------------------------------------------------------------

from sagemaker.jumpstart.notebook_utils import list_jumpstart_models

text_generation_models = list_jumpstart_models(filter_value="task == txt2txt")
print(f"\nテキスト生成モデル数: {len(text_generation_models)}")
print("主なモデル（最初の10件）:")
for model_id in text_generation_models[:10]:
    print(f"  - {model_id}")

# ---------------------------------------------------------------------------
# 7. テストデータの削除
# ---------------------------------------------------------------------------

s3_client.delete_object(Bucket=bucket, Key=f"{prefix}/test_data.json")
print("\nテストデータを削除しました")
