# =============================================================================
# Amazon SageMaker #6 — Model Registry の確認と承認
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #6】SageMaker PipelinesでMLOpsパイプラインを
#              構築してみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
パイプラインで登録されたモデルパッケージを確認し、
手動承認（Approved）に更新する。
"""

import boto3

sm_client = boto3.client("sagemaker")
model_package_group_name = "income-prediction-models"

# ---------------------------------------------------------------------------
# 1. モデルパッケージの一覧
# ---------------------------------------------------------------------------

response = sm_client.list_model_packages(
    ModelPackageGroupName=model_package_group_name,
    SortBy="CreationTime",
    SortOrder="Descending",
)

print("登録済みモデル一覧:")
for pkg in response["ModelPackageSummaryList"]:
    print(f"  ARN: {pkg['ModelPackageArn']}")
    print(f"  ステータス: {pkg['ModelApprovalStatus']}")
    print(f"  作成日時: {pkg['CreationTime']}")
    print()

# ---------------------------------------------------------------------------
# 2. 最新モデルの詳細確認
# ---------------------------------------------------------------------------

if response["ModelPackageSummaryList"]:
    latest_arn = response["ModelPackageSummaryList"][0]["ModelPackageArn"]
    detail = sm_client.describe_model_package(ModelPackageName=latest_arn)

    print("最新モデルの詳細:")
    print(f"  承認ステータス: {detail['ModelApprovalStatus']}")

    # 評価メトリクスがあれば表示
    if "ModelMetrics" in detail:
        print(f"  モデルメトリクス: {detail['ModelMetrics']}")

    # ---------------------------------------------------------------------------
    # 3. モデルの承認
    # ---------------------------------------------------------------------------

    sm_client.update_model_package(
        ModelPackageArn=latest_arn,
        ModelApprovalStatus="Approved",
    )
    print(f"\n  ステータスを 'Approved' に更新しました: {latest_arn}")

else:
    print("登録済みモデルがありません。パイプラインを先に実行してください。")
