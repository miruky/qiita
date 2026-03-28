# =============================================================================
# Amazon SageMaker #6 — SageMaker Pipelines パイプラインの定義と実行
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #6】SageMaker PipelinesでMLOpsパイプラインを
#              構築してみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: 前処理済みデータが S3 に存在すること
# =============================================================================

"""
SageMaker Pipelines で MLOps パイプラインを構築する。
前処理 → トレーニング → 評価 → 条件分岐 → モデル登録の一連の流れを自動化する。
"""

import json
import sagemaker
import boto3
from sagemaker import image_uris
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet
from sagemaker.workflow.properties import PropertyFile
from sagemaker.workflow.parameters import (
    ParameterString,
    ParameterFloat,
    ParameterInteger,
)

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
role = sagemaker.get_execution_role()

# ---------------------------------------------------------------------------
# 2. パイプラインパラメータの定義
# ---------------------------------------------------------------------------

processing_instance_type = ParameterString(
    name="ProcessingInstanceType", default_value="ml.m5.large"
)
training_instance_type = ParameterString(
    name="TrainingInstanceType", default_value="ml.m5.large"
)
model_approval_status = ParameterString(
    name="ModelApprovalStatus", default_value="PendingManualApproval"
)
auc_threshold = ParameterFloat(name="AucThreshold", default_value=0.7)
max_depth = ParameterInteger(name="MaxDepth", default_value=5)

# ---------------------------------------------------------------------------
# 3. 前処理ステップ
# ---------------------------------------------------------------------------

sklearn_image = image_uris.retrieve(
    framework="sklearn",
    region=session.boto_region_name,
    version="1.2-1",
)

preprocessing_processor = ScriptProcessor(
    role=role,
    image_uri=sklearn_image,
    command=["python3"],
    instance_type=processing_instance_type,
    instance_count=1,
    base_job_name="pipeline-preprocessing",
)

step_preprocess = ProcessingStep(
    name="Preprocessing",
    processor=preprocessing_processor,
    code="preprocessing.py",
    inputs=[
        ProcessingInput(
            source=f"s3://{bucket}/{prefix}/processing/input/raw_data.csv",
            destination="/opt/ml/processing/input/raw_data.csv",
        )
    ],
    outputs=[
        ProcessingOutput(
            output_name="train",
            source="/opt/ml/processing/output/train.csv",
            destination=f"s3://{bucket}/{prefix}/pipeline/train",
        ),
        ProcessingOutput(
            output_name="validation",
            source="/opt/ml/processing/output/validation.csv",
            destination=f"s3://{bucket}/{prefix}/pipeline/validation",
        ),
        ProcessingOutput(
            output_name="test",
            source="/opt/ml/processing/output/test.csv",
            destination=f"s3://{bucket}/{prefix}/pipeline/test",
        ),
    ],
)

# ---------------------------------------------------------------------------
# 4. トレーニングステップ
# ---------------------------------------------------------------------------

xgboost_image = image_uris.retrieve(
    framework="xgboost",
    region=session.boto_region_name,
    version="1.7-1",
)

xgb_estimator = Estimator(
    image_uri=xgboost_image,
    role=role,
    instance_count=1,
    instance_type=training_instance_type,
    output_path=f"s3://{bucket}/{prefix}/pipeline/model",
)

xgb_estimator.set_hyperparameters(
    objective="binary:logistic",
    num_round=100,
    max_depth=max_depth,
    eta=0.2,
    gamma=4,
    min_child_weight=6,
    subsample=0.8,
    eval_metric="auc",
)

step_train = TrainingStep(
    name="TrainXGBoost",
    estimator=xgb_estimator,
    inputs={
        "train": TrainingInput(
            s3_data=step_preprocess.properties.ProcessingOutputConfig.Outputs[
                "train"
            ].S3Output.S3Uri,
            content_type="text/csv",
        ),
        "validation": TrainingInput(
            s3_data=step_preprocess.properties.ProcessingOutputConfig.Outputs[
                "validation"
            ].S3Output.S3Uri,
            content_type="text/csv",
        ),
    },
)

# ---------------------------------------------------------------------------
# 5. 評価ステップ
# ---------------------------------------------------------------------------

evaluation_report = PropertyFile(
    name="EvaluationReport",
    output_name="evaluation",
    path="evaluation.json",
)

eval_processor = ScriptProcessor(
    role=role,
    image_uri=sklearn_image,
    command=["python3"],
    instance_type=processing_instance_type,
    instance_count=1,
    base_job_name="pipeline-evaluation",
)

step_eval = ProcessingStep(
    name="EvaluateModel",
    processor=eval_processor,
    code="evaluation.py",
    inputs=[
        ProcessingInput(
            source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
            destination="/opt/ml/processing/model",
        ),
        ProcessingInput(
            source=step_preprocess.properties.ProcessingOutputConfig.Outputs[
                "test"
            ].S3Output.S3Uri,
            destination="/opt/ml/processing/test",
        ),
    ],
    outputs=[
        ProcessingOutput(
            output_name="evaluation",
            source="/opt/ml/processing/evaluation",
        ),
    ],
    property_files=[evaluation_report],
)

# ---------------------------------------------------------------------------
# 6. 条件分岐ステップ（AUC ≥ しきい値 で登録）
# ---------------------------------------------------------------------------

condition_auc = ConditionGreaterThanOrEqualTo(
    left=JsonGet(
        step_name=step_eval.name,
        property_file=evaluation_report,
        json_path="metrics.auc.value",
    ),
    right=auc_threshold,
)

# ---------------------------------------------------------------------------
# 7. モデル登録ステップ
# ---------------------------------------------------------------------------

step_register = RegisterModel(
    name="RegisterModel",
    estimator=xgb_estimator,
    model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
    content_types=["text/csv"],
    response_types=["text/csv"],
    inference_instances=["ml.m5.large", "ml.m5.xlarge"],
    transform_instances=["ml.m5.large"],
    model_package_group_name="income-prediction-models",
    approval_status=model_approval_status,
)

step_condition = ConditionStep(
    name="CheckAucThreshold",
    conditions=[condition_auc],
    if_steps=[step_register],
    else_steps=[],
)

# ---------------------------------------------------------------------------
# 8. パイプラインの定義と実行
# ---------------------------------------------------------------------------

pipeline = Pipeline(
    name="income-prediction-pipeline",
    parameters=[
        processing_instance_type,
        training_instance_type,
        model_approval_status,
        auc_threshold,
        max_depth,
    ],
    steps=[step_preprocess, step_train, step_eval, step_condition],
    sagemaker_session=session,
)

# パイプライン定義を確認
definition = json.loads(pipeline.definition())
print("パイプラインステップ:")
for step in definition["Steps"]:
    print(f"  - {step['Name']} ({step['Type']})")

# パイプラインの作成/更新
pipeline.upsert(role_arn=role)
print("\nパイプラインを作成/更新しました。")

# パイプラインの実行
execution = pipeline.start()
print(f"パイプライン実行開始: {execution.arn}")
print("（完了まで約15〜20分かかります）")

execution.wait()
print("パイプライン実行完了！")

# 実行結果の確認
for step in execution.list_steps():
    print(f"  {step['StepName']}: {step['StepStatus']}")
