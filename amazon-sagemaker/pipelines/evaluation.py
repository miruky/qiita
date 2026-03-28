# =============================================================================
# Amazon SageMaker #6 — パイプライン用モデル評価スクリプト
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #6】SageMaker PipelinesでMLOpsパイプラインを
#              構築してみる
#
# このスクリプトは Processing Job のコンテナ内で実行される。
# 入力: /opt/ml/processing/model/ にモデル、/opt/ml/processing/test/ にテストデータ
# 出力: /opt/ml/processing/evaluation/evaluation.json
#
# 実行コンテナ: sklearn 1.2-1 イメージ
# 注意: sklearn コンテナには xgboost が含まれていないため、
#       スクリプト内で pip install する必要がある。
# =============================================================================

"""
SageMaker Pipelines の評価ステップで実行するスクリプト。
モデルをロードしてテストデータで推論し、評価メトリクスを JSON で出力する。
"""

import json
import os
import subprocess
import sys
import tarfile

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# xgboost のインストール（sklearn コンテナにはプリインストールされていない）
# ---------------------------------------------------------------------------
subprocess.check_call([sys.executable, "-m", "pip", "install", "xgboost", "-q"])
import xgboost as xgb

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


def evaluate():
    """モデルを評価して evaluation.json を出力する"""

    # モデルの解凍とロード
    model_path = "/opt/ml/processing/model/model.tar.gz"
    with tarfile.open(model_path) as tar:
        tar.extractall(path="/opt/ml/processing/model")

    model = xgb.Booster()
    model.load_model("/opt/ml/processing/model/xgboost-model")

    # テストデータの読み込み
    test_path = "/opt/ml/processing/test/test.csv"
    test_df = pd.read_csv(test_path, header=None)

    # 先頭列が目的変数
    y_test = test_df.iloc[:, 0].values
    X_test = test_df.iloc[:, 1:].values

    # 推論
    dtest = xgb.DMatrix(X_test)
    predictions = model.predict(dtest)
    pred_labels = (predictions >= 0.5).astype(int)

    # 評価メトリクスの算出
    evaluation = {
        "metrics": {
            "accuracy": {"value": float(accuracy_score(y_test, pred_labels))},
            "precision": {"value": float(precision_score(y_test, pred_labels))},
            "recall": {"value": float(recall_score(y_test, pred_labels))},
            "f1": {"value": float(f1_score(y_test, pred_labels))},
            "auc": {"value": float(roc_auc_score(y_test, predictions))},
        }
    }

    # 結果を JSON で保存
    output_dir = "/opt/ml/processing/evaluation"
    os.makedirs(output_dir, exist_ok=True)

    eval_path = os.path.join(output_dir, "evaluation.json")
    with open(eval_path, "w") as f:
        json.dump(evaluation, f, indent=2)

    print("評価結果:")
    for metric_name, metric_data in evaluation["metrics"].items():
        print(f"  {metric_name}: {metric_data['value']:.4f}")

    return evaluation


if __name__ == "__main__":
    evaluate()
