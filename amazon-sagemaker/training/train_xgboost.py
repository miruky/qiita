# =============================================================================
# Amazon SageMaker #4 — XGBoost 組み込みアルゴリズムでのトレーニング
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #4】組み込みアルゴリズムXGBoostでモデルを
#              トレーニングしてみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: Processing Job で前処理済みの train/validation/test データが S3 にある
# 使用アルゴリズム: XGBoost 1.7-1（SageMaker 組み込み）
# =============================================================================

"""
SageMaker 組み込み XGBoost で二値分類モデルをトレーニングする。
CSV データの読み込み → XGBoost 用フォーマット変換 → Estimator 設定 → 学習 → 結果確認。
"""

import pandas as pd
import numpy as np
import sagemaker
import boto3
from sagemaker import image_uris
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
role = sagemaker.get_execution_role()

print(f"バケット: {bucket}")
print(f"ロール: {role}")

# ---------------------------------------------------------------------------
# 2. データの確認と XGBoost 用フォーマット変換
# ---------------------------------------------------------------------------

# 前処理済みデータの確認
train_df = pd.read_csv(f"s3://{bucket}/{prefix}/processing/output/train.csv")
val_df = pd.read_csv(f"s3://{bucket}/{prefix}/processing/output/validation.csv")
test_df = pd.read_csv(f"s3://{bucket}/{prefix}/processing/output/test.csv")

print(f"トレーニング: {train_df.shape}")
print(f"検証: {val_df.shape}")
print(f"テスト: {test_df.shape}")

# XGBoost 用にフォーマット変換（目的変数を先頭列に移動、ヘッダーなし）
target_col = "income"

for name, df in [("train", train_df), ("validation", val_df), ("test", test_df)]:
    # 目的変数を先頭にする
    cols = [target_col] + [c for c in df.columns if c != target_col]
    df_xgb = df[cols]

    # ヘッダーなし CSV で保存
    output_path = f"s3://{bucket}/{prefix}/xgboost/{name}/data.csv"
    df_xgb.to_csv(output_path, index=False, header=False)
    print(f"{name} データアップロード完了: {output_path}")

# ---------------------------------------------------------------------------
# 3. XGBoost コンテナイメージの取得
# ---------------------------------------------------------------------------

xgboost_image = image_uris.retrieve(
    framework="xgboost",
    region=session.boto_region_name,
    version="1.7-1",
)
print(f"\nXGBoost イメージ: {xgboost_image}")

# ---------------------------------------------------------------------------
# 4. Estimator の設定
# ---------------------------------------------------------------------------

xgb_estimator = Estimator(
    image_uri=xgboost_image,
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",
    output_path=f"s3://{bucket}/{prefix}/xgboost/model",
    sagemaker_session=session,
    base_job_name="xgboost-income-prediction",
)

# ハイパーパラメータの設定
xgb_estimator.set_hyperparameters(
    objective="binary:logistic",   # 二値分類
    num_round=100,                 # ブースティングラウンド数
    max_depth=5,                   # 木の最大深さ
    eta=0.2,                       # 学習率
    gamma=4,                       # 分割の最小損失減少
    min_child_weight=6,            # 子ノードの最小重み
    subsample=0.8,                 # データのサンプリング率
    eval_metric="auc",             # 評価指標
)

print("\nハイパーパラメータ:")
for key, value in xgb_estimator.hyperparameters().items():
    print(f"  {key}: {value}")

# ---------------------------------------------------------------------------
# 5. トレーニング入力データの設定
# ---------------------------------------------------------------------------

train_input = TrainingInput(
    s3_data=f"s3://{bucket}/{prefix}/xgboost/train/",
    content_type="text/csv",
)
validation_input = TrainingInput(
    s3_data=f"s3://{bucket}/{prefix}/xgboost/validation/",
    content_type="text/csv",
)

# ---------------------------------------------------------------------------
# 6. トレーニング実行
# ---------------------------------------------------------------------------

print("\nトレーニング開始...")
xgb_estimator.fit(
    {"train": train_input, "validation": validation_input},
    wait=True,
    logs="All",
)

print(f"\nトレーニングジョブ名: {xgb_estimator.latest_training_job.name}")
print(f"モデル出力先: {xgb_estimator.output_path}")

# ---------------------------------------------------------------------------
# 7. 結果確認
# ---------------------------------------------------------------------------

training_job_name = xgb_estimator.latest_training_job.name
sm_client = boto3.client("sagemaker")

training_job_info = sm_client.describe_training_job(TrainingJobName=training_job_name)

print(f"\nトレーニングジョブ詳細:")
print(f"  ステータス: {training_job_info['TrainingJobStatus']}")
print(f"  実行時間: {training_job_info['TrainingEndTime'] - training_job_info['TrainingStartTime']}")
print(f"  課金時間: {training_job_info['BillableTimeInSeconds']}秒")

# メトリクスの確認
for metric in training_job_info.get("FinalMetricDataList", []):
    print(f"  {metric['MetricName']}: {metric['Value']:.4f}")
