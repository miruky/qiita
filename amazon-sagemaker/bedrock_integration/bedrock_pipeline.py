# =============================================================================
# Amazon SageMaker #8 — SageMaker Pipelines + Bedrock 連携パイプライン
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #8】SageMaker AIとBedrockを連携させて実践活用
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: bedrock_analysis.py が同じディレクトリに存在すること
# =============================================================================

"""
SageMaker Pipelines で前処理 → Bedrock 分析 → 結果出力のパイプラインを構築する。
"""

import sagemaker
import boto3
from sagemaker import image_uris
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep
from sagemaker.workflow.parameters import ParameterString

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson/bedrock-integration"
role = sagemaker.get_execution_role()

# ---------------------------------------------------------------------------
# 2. パラメータ定義
# ---------------------------------------------------------------------------

input_data_uri = ParameterString(
    name="InputDataUri",
    default_value=f"s3://{bucket}/{prefix}/reviews/processed_reviews.csv",
)

processing_instance_type = ParameterString(
    name="ProcessingInstanceType",
    default_value="ml.m5.large",
)

# ---------------------------------------------------------------------------
# 3. Bedrock 分析ステップ
# ---------------------------------------------------------------------------

sklearn_image = image_uris.retrieve(
    framework="sklearn",
    region=session.boto_region_name,
    version="1.2-1",
)

bedrock_processor = ScriptProcessor(
    role=role,
    image_uri=sklearn_image,
    command=["python3"],
    instance_type=processing_instance_type,
    instance_count=1,
    base_job_name="bedrock-analysis",
    env={"AWS_DEFAULT_REGION": session.boto_region_name},
)

step_bedrock_analysis = ProcessingStep(
    name="BedrockAnalysis",
    processor=bedrock_processor,
    code="bedrock_analysis.py",
    inputs=[
        ProcessingInput(
            source=input_data_uri,
            destination="/opt/ml/processing/input/reviews.csv",
        )
    ],
    outputs=[
        ProcessingOutput(
            output_name="analyzed_data",
            source="/opt/ml/processing/output",
            destination=f"s3://{bucket}/{prefix}/pipeline-output",
        )
    ],
)

# ---------------------------------------------------------------------------
# 4. パイプライン定義と実行
# ---------------------------------------------------------------------------

pipeline = Pipeline(
    name="bedrock-review-analysis-pipeline",
    parameters=[input_data_uri, processing_instance_type],
    steps=[step_bedrock_analysis],
    sagemaker_session=session,
)

pipeline.upsert(role_arn=role)
print("パイプラインを作成しました。")

execution = pipeline.start()
print(f"パイプライン実行開始: {execution.arn}")
print("（完了まで数分かかります）")

execution.wait()
print("パイプライン完了！")

for step in execution.list_steps():
    print(f"  {step['StepName']}: {step['StepStatus']}")
