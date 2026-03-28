# =============================================================================
# Amazon SageMaker #3 — サンプルデータの作成と探索的データ分析（EDA）
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #3】Processing JobとData Wranglerでデータ前処理を
#              やってみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
Adult Census Income 風のサンプルデータを作成し、
探索的データ分析（EDA）を実施するスクリプト。
"""

import pandas as pd
import numpy as np
import sagemaker
import boto3

# ---------------------------------------------------------------------------
# 1. SageMaker セッション
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson/processing"
role = sagemaker.get_execution_role()

print(f"バケット: {bucket}")
print(f"ロール: {role}")

# ---------------------------------------------------------------------------
# 2. サンプルデータの作成（Adult Census Income 風）
# ---------------------------------------------------------------------------

np.random.seed(42)
n_samples = 1000

data = {
    "age": np.random.randint(17, 90, n_samples),
    "workclass": np.random.choice(
        ["Private", "Self-emp", "Gov", "Without-pay", None],
        n_samples,
        p=[0.7, 0.1, 0.1, 0.05, 0.05],
    ),
    "education": np.random.choice(
        ["Bachelors", "Masters", "HS-grad", "Some-college", "Doctorate"],
        n_samples,
    ),
    "education_num": np.random.randint(1, 17, n_samples),
    "marital_status": np.random.choice(
        ["Married", "Never-married", "Divorced", "Separated"],
        n_samples,
    ),
    "occupation": np.random.choice(
        ["Tech-support", "Sales", "Exec-managerial", "Prof-specialty", "Craft-repair", None],
        n_samples,
        p=[0.15, 0.2, 0.2, 0.2, 0.2, 0.05],
    ),
    "hours_per_week": np.random.randint(1, 99, n_samples),
    "income": np.random.choice(["<=50K", ">50K"], n_samples, p=[0.75, 0.25]),
}

df = pd.DataFrame(data)

# 意図的にデータ品質の問題を作る
# 1. 欠損値（NaN）を追加
df.loc[np.random.choice(n_samples, 30, replace=False), "age"] = np.nan
df.loc[np.random.choice(n_samples, 20, replace=False), "hours_per_week"] = np.nan

# 2. 異常値を追加
df.loc[np.random.choice(n_samples, 5, replace=False), "age"] = 150
df.loc[np.random.choice(n_samples, 3, replace=False), "hours_per_week"] = 200

# 3. 重複行を追加
duplicates = df.sample(20, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

print(f"データセットのサイズ: {df.shape}")
print(f"\n最初の5行:")
print(df.head())

# ---------------------------------------------------------------------------
# 3. 探索的データ分析（EDA）
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print("データ型と欠損値の確認")
print("=" * 50)
print(df.info())

print("\n" + "=" * 50)
print("数値カラムの統計量")
print("=" * 50)
print(df.describe())

print("\n" + "=" * 50)
print("欠損値の数")
print("=" * 50)
print(df.isnull().sum())

print("\n" + "=" * 50)
print("重複行の数")
print("=" * 50)
print(f"重複行: {df.duplicated().sum()}件")

# ---------------------------------------------------------------------------
# 4. CSV として保存 & S3 にアップロード
# ---------------------------------------------------------------------------

df.to_csv("raw_data.csv", index=False)
input_data_path = f"s3://{bucket}/{prefix}/input/raw_data.csv"
sagemaker.s3.S3Uploader.upload("raw_data.csv", f"s3://{bucket}/{prefix}/input")
print(f"\n入力データをアップロード: {input_data_path}")
