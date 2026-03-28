# =============================================================================
# Amazon SageMaker #5 — エンドポイント・モデルの一括削除
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #5】4つの推論方式を比較しながらモデルをデプロイ
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
ハンズオンで作成したエンドポイント・エンドポイント設定・モデルを一括削除する。
課金の継続を防ぐため、使い終わったら必ず実行すること。
"""

import boto3

sm_client = boto3.client("sagemaker")

# ---------------------------------------------------------------------------
# 1. 削除対象のエンドポイント
# ---------------------------------------------------------------------------

endpoints_to_delete = [
    "xgboost-income-realtime",
    "xgboost-income-serverless",
]

for endpoint_name in endpoints_to_delete:
    try:
        # エンドポイントの削除
        sm_client.delete_endpoint(EndpointName=endpoint_name)
        print(f"エンドポイント削除: {endpoint_name}")

        # エンドポイント設定の削除
        sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
        print(f"エンドポイント設定削除: {endpoint_name}")
    except sm_client.exceptions.ClientError as e:
        if "Could not find" in str(e):
            print(f"スキップ（存在しない）: {endpoint_name}")
        else:
            raise

# ---------------------------------------------------------------------------
# 2. モデルの削除
# ---------------------------------------------------------------------------

models_to_delete = [
    "xgboost-income-model",
]

for model_name in models_to_delete:
    try:
        sm_client.delete_model(ModelName=model_name)
        print(f"モデル削除: {model_name}")
    except sm_client.exceptions.ClientError as e:
        if "Could not find" in str(e):
            print(f"スキップ（存在しない）: {model_name}")
        else:
            raise

print("\nクリーンアップ完了！")
