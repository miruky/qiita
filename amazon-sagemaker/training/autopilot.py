# =============================================================================
# Amazon SageMaker #4 — Autopilot（AutoML）で自動トレーニング
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #4】組み込みアルゴリズムXGBoostでモデルを
#              トレーニングしてみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
SageMaker Autopilot（AutoML V2）で自動的に最適なモデルを探索・トレーニングする。
"""

import sagemaker
import boto3
from sagemaker.automl.automl import AutoML

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
role = sagemaker.get_execution_role()

# ---------------------------------------------------------------------------
# 2. Autopilot の設定
# ---------------------------------------------------------------------------

automl = AutoML(
    role=role,
    target_attribute_name="income",
    sagemaker_session=session,
    total_job_runtime_in_seconds=3600,  # 最大1時間
    mode="ENSEMBLING",                  # アンサンブルモード
    max_candidates=10,                  # 最大候補モデル数
)

# ---------------------------------------------------------------------------
# 3. Autopilot の実行
# ---------------------------------------------------------------------------

train_data = f"s3://{bucket}/{prefix}/processing/output/train.csv"

print("Autopilot ジョブ開始...")
print("（完了まで数十分〜1時間程度かかります）")

automl.fit(
    inputs=train_data,
    wait=True,
    logs=True,
)

# ---------------------------------------------------------------------------
# 4. 結果の確認
# ---------------------------------------------------------------------------

best_candidate = automl.best_candidate()
print(f"\nベストモデル名: {best_candidate['CandidateName']}")
print(f"目的指標: {best_candidate['FinalAutoMLJobObjectiveMetric']}")
print(f"推論コンテナ数: {len(best_candidate['InferenceContainers'])}")
