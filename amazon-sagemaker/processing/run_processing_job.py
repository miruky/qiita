# =============================================================================
# Amazon SageMaker #3 — Processing Job の起動と結果確認
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #3】Processing JobとData Wranglerでデータ前処理を
#              やってみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: prepare_sample_data.py を先に実行し、S3 にデータをアップロード済み
# =============================================================================

"""
ScriptProcessor で前処理スクリプト (preprocessing.py) を実行し、
処理結果を S3 からダウンロードして確認する。
"""

import pandas as pd
import sagemaker
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson/processing"
role = sagemaker.get_execution_role()

input_data_path = f"s3://{bucket}/{prefix}/input/raw_data.csv"
print(f"入力データ: {input_data_path}")

# ---------------------------------------------------------------------------
# 2. ScriptProcessor の設定と実行
# ---------------------------------------------------------------------------

script_processor = ScriptProcessor(
    role=role,
    image_uri=sagemaker.image_uris.retrieve(
        framework="sklearn",
        region=session.boto_region_name,
        version="1.2-1",
    ),
    command=["python3"],
    instance_type="ml.m5.large",
    instance_count=1,
    base_job_name="sagemaker-handson-preprocessing",
)

# Processing Job の実行
script_processor.run(
    code="preprocessing.py",
    inputs=[
        ProcessingInput(
            source=input_data_path,
            destination="/opt/ml/processing/input/raw_data.csv",
            s3_data_type="S3Prefix",
            s3_input_mode="File",
        )
    ],
    outputs=[
        ProcessingOutput(
            output_name="processed_data",
            source="/opt/ml/processing/output",
            destination=f"s3://{bucket}/{prefix}/output",
        )
    ],
)

print("Processing Job が完了しました！")

# ---------------------------------------------------------------------------
# 3. 処理結果の確認
# ---------------------------------------------------------------------------

train_df = pd.read_csv(f"s3://{bucket}/{prefix}/output/train.csv")
val_df = pd.read_csv(f"s3://{bucket}/{prefix}/output/validation.csv")
test_df = pd.read_csv(f"s3://{bucket}/{prefix}/output/test.csv")

print("\n処理済みデータの確認")
print(f"トレーニング: {train_df.shape}")
print(f"検証: {val_df.shape}")
print(f"テスト: {test_df.shape}")

print(f"\n欠損値の合計: {train_df.isnull().sum().sum()}")
print(f"\nカラム一覧:")
for col in train_df.columns:
    print(f"  - {col}")
