# =============================================================================
# Amazon SageMaker #7 — DistilBERT のファインチューニング（感情分析）
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #7】JumpStartで基盤モデルをサクッと活用してみる
#
# 実行環境: SageMaker Studio JupyterLab
# 注意: ファインチューニングには ml.g5.2xlarge（GPU）が必要。
# =============================================================================

"""
JumpStart の DistilBERT（テキスト分類モデル）を
日本語感情分析データセットでファインチューニングし、デプロイする。
"""

import json
import sagemaker
from sagemaker.jumpstart.estimator import JumpStartEstimator
from sagemaker.jumpstart.model import JumpStartModel

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson/jumpstart"
role = sagemaker.get_execution_role()

# ---------------------------------------------------------------------------
# 2. トレーニングデータの準備
# ---------------------------------------------------------------------------

# 感情分析用のサンプルデータ（実際は大量データを用意する想定）
train_data = [
    {"text": "この製品は素晴らしい品質です。大満足！", "label": 1},
    {"text": "期待外れでした。二度と購入しません。", "label": 0},
    {"text": "コスパが良くておすすめです。", "label": 1},
    {"text": "配送が遅くて困りました。", "label": 0},
    {"text": "デザインが美しく、使い心地も最高です。", "label": 1},
    {"text": "すぐに壊れてしまいました。", "label": 0},
    {"text": "家族みんなで気に入っています。", "label": 1},
    {"text": "説明と違う商品が届きました。", "label": 0},
]

import pandas as pd

train_df = pd.DataFrame(train_data)
train_path = f"s3://{bucket}/{prefix}/finetune/train.csv"
train_df.to_csv(train_path, index=False)
print(f"トレーニングデータ: {train_path}")

# ---------------------------------------------------------------------------
# 3. JumpStart Estimator でファインチューニング
# ---------------------------------------------------------------------------

model_id = "huggingface-tc-distilbert-base-uncased"  # テキスト分類

estimator = JumpStartEstimator(
    model_id=model_id,
    role=role,
    instance_type="ml.g5.2xlarge",
    instance_count=1,
    hyperparameters={
        "epochs": "3",
        "learning_rate": "2e-5",
        "batch_size": "8",
    },
)

print("ファインチューニング開始...")

estimator.fit(
    {"training": train_path},
    wait=True,
)

print("ファインチューニング完了！")

# ---------------------------------------------------------------------------
# 4. ファインチューニング済みモデルのデプロイ
# ---------------------------------------------------------------------------

predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.xlarge",
)

print(f"デプロイ完了！ エンドポイント: {predictor.endpoint_name}")

# ---------------------------------------------------------------------------
# 5. 推論テスト
# ---------------------------------------------------------------------------

test_texts = [
    "とても使いやすくて満足しています。",
    "品質が悪く、返品を検討中です。",
    "価格以上の価値があります。",
]

for text in test_texts:
    response = predictor.predict({"inputs": text})
    print(f"テキスト: {text}")
    print(f"結果: {response}")
    print()

# ---------------------------------------------------------------------------
# 6. クリーンアップ
# ---------------------------------------------------------------------------

# predictor.delete_endpoint()
# print("エンドポイントを削除しました。")
