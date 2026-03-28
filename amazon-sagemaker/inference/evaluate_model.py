# =============================================================================
# Amazon SageMaker #5 — モデル精度の評価
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #5】4つの推論方式を比較しながらモデルをデプロイ
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
リアルタイムエンドポイント経由で全テストデータに推論を行い、
Accuracy / Precision / Recall / F1 / AUC を算出する。
"""

import pandas as pd
import numpy as np
import sagemaker
import boto3
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
runtime_client = boto3.client("sagemaker-runtime")
endpoint_name = "xgboost-income-realtime"

# ---------------------------------------------------------------------------
# 2. テストデータの読み込みと推論
# ---------------------------------------------------------------------------

test_df = pd.read_csv(f"s3://{bucket}/{prefix}/processing/output/test.csv")
target_col = "income"
feature_cols = [c for c in test_df.columns if c != target_col]
test_labels = test_df[target_col].values

# CSV に変換して推論
csv_payload = test_df[feature_cols].to_csv(index=False, header=False)
response = runtime_client.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType="text/csv",
    Body=csv_payload,
)

raw_predictions = response["Body"].read().decode("utf-8").strip().split("\n")
predictions = np.array([float(p) for p in raw_predictions])
pred_labels = (predictions >= 0.5).astype(int)

# ---------------------------------------------------------------------------
# 3. 評価メトリクスの算出
# ---------------------------------------------------------------------------

print("=" * 50)
print("モデル評価結果")
print("=" * 50)
print(f"テストデータ数: {len(test_labels)}")
print(f"\nAccuracy:  {accuracy_score(test_labels, pred_labels):.4f}")
print(f"Precision: {precision_score(test_labels, pred_labels):.4f}")
print(f"Recall:    {recall_score(test_labels, pred_labels):.4f}")
print(f"F1 Score:  {f1_score(test_labels, pred_labels):.4f}")
print(f"AUC:       {roc_auc_score(test_labels, predictions):.4f}")

# ---------------------------------------------------------------------------
# 4. 混同行列
# ---------------------------------------------------------------------------

cm = confusion_matrix(test_labels, pred_labels)
print(f"\n混同行列:")
print(f"  TN={cm[0][0]:4d}  FP={cm[0][1]:4d}")
print(f"  FN={cm[1][0]:4d}  TP={cm[1][1]:4d}")

# ---------------------------------------------------------------------------
# 5. 詳細レポート
# ---------------------------------------------------------------------------

print(f"\n分類レポート:")
print(classification_report(test_labels, pred_labels, target_names=["低所得", "高所得"]))
