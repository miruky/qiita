# =============================================================================
# Amazon SageMaker #4 — ハイパーパラメータチューニング（HPO）
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #4】組み込みアルゴリズムXGBoostでモデルを
#              トレーニングしてみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: train_xgboost.py と同じデータが S3 に存在すること
# =============================================================================

"""
SageMaker HyperparameterTuner によるベイズ最適化チューニング。
XGBoost の主要パラメータ（max_depth, eta, min_child_weight, subsample, num_round）を自動探索する。
"""

import sagemaker
from sagemaker import image_uris
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput
from sagemaker.tuner import (
    HyperparameterTuner,
    IntegerParameter,
    ContinuousParameter,
)

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
role = sagemaker.get_execution_role()

xgboost_image = image_uris.retrieve(
    framework="xgboost",
    region=session.boto_region_name,
    version="1.7-1",
)

# ---------------------------------------------------------------------------
# 2. ベース Estimator の設定
# ---------------------------------------------------------------------------

xgb_estimator = Estimator(
    image_uri=xgboost_image,
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",
    output_path=f"s3://{bucket}/{prefix}/xgboost/tuning",
    sagemaker_session=session,
)

xgb_estimator.set_hyperparameters(
    objective="binary:logistic",
    eval_metric="auc",
    gamma=4,
)

# ---------------------------------------------------------------------------
# 3. ハイパーパラメータの探索範囲を定義
# ---------------------------------------------------------------------------

hyperparameter_ranges = {
    "max_depth": IntegerParameter(3, 10),
    "eta": ContinuousParameter(0.01, 0.5),
    "min_child_weight": IntegerParameter(1, 10),
    "subsample": ContinuousParameter(0.5, 1.0),
    "num_round": IntegerParameter(50, 300),
}

# ---------------------------------------------------------------------------
# 4. Tuner の設定
# ---------------------------------------------------------------------------

tuner = HyperparameterTuner(
    estimator=xgb_estimator,
    objective_metric_name="validation:auc",
    hyperparameter_ranges=hyperparameter_ranges,
    max_jobs=10,           # 合計ジョブ数
    max_parallel_jobs=2,   # 同時実行数
    strategy="Bayesian",   # ベイズ最適化
)

# ---------------------------------------------------------------------------
# 5. チューニング実行
# ---------------------------------------------------------------------------

train_input = TrainingInput(
    s3_data=f"s3://{bucket}/{prefix}/xgboost/train/",
    content_type="text/csv",
)
validation_input = TrainingInput(
    s3_data=f"s3://{bucket}/{prefix}/xgboost/validation/",
    content_type="text/csv",
)

print("ハイパーパラメータチューニング開始...")
print("（約20〜30分かかります）")

tuner.fit(
    {"train": train_input, "validation": validation_input},
    wait=True,
)

# ---------------------------------------------------------------------------
# 6. チューニング結果の確認
# ---------------------------------------------------------------------------

tuner_results = tuner.analytics().dataframe()
print("\nチューニング結果（AUC上位5件）:")
print(
    tuner_results.sort_values("FinalObjectiveValue", ascending=False)
    .head()
    .to_string()
)

print(f"\nベストモデルのジョブ名: {tuner.best_training_job()}")
