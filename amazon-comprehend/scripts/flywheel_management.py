# Amazon Comprehend #3 — フライホイールによるモデル管理
# ファイル: flywheel_management.py
# 概要: カスタムモデルのバージョン管理とトレーニングプロセスを自動化する
#       フライホイール機能の作成・イテレーション実行を行う。

import boto3

comprehend = boto3.client("comprehend", region_name="ap-northeast-1")


def create_flywheel(flywheel_name, active_model_arn, data_access_role_arn, data_lake_s3_uri):
    """フライホイールを作成する。

    Parameters
    ----------
    flywheel_name : str
        フライホイール名
    active_model_arn : str
        現在アクティブなモデルの ARN
    data_access_role_arn : str
        S3 アクセス用 IAM ロールの ARN
    data_lake_s3_uri : str
        データレイクの S3 URI

    Returns
    -------
    str
        フライホイールの ARN
    """
    response = comprehend.create_flywheel(
        FlywheelName=flywheel_name,
        ActiveModelArn=active_model_arn,
        DataAccessRoleArn=data_access_role_arn,
        DataLakeS3Uri=data_lake_s3_uri,
    )

    flywheel_arn = response["FlywheelArn"]
    print(f"フライホイールARN: {flywheel_arn}")
    return flywheel_arn


def start_iteration(flywheel_arn):
    """フライホイールのイテレーションを実行する。

    新しいトレーニングデータが蓄積されたら呼び出し、
    モデルを最新データで再トレーニングする。

    Parameters
    ----------
    flywheel_arn : str
        フライホイールの ARN

    Returns
    -------
    str
        イテレーションID
    """
    response = comprehend.start_flywheel_iteration(
        FlywheelArn=flywheel_arn
    )
    iteration_id = response["FlywheelIterationId"]
    print(f"イテレーションID: {iteration_id}")
    return iteration_id


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    CLASSIFIER_ARN = "arn:aws:comprehend:ap-northeast-1:123456789012:document-classifier/customer-support-classifier"

    fw_arn = create_flywheel(
        flywheel_name="support-classifier-flywheel",
        active_model_arn=CLASSIFIER_ARN,
        data_access_role_arn="arn:aws:iam::123456789012:role/ComprehendDataAccessRole",
        data_lake_s3_uri="s3://my-comprehend-bucket/flywheel-data/",
    )

    # 新しいデータが蓄積されたらイテレーションを実行
    # start_iteration(fw_arn)
