# =============================================================================
# Amazon SageMaker #3 — Processing Job で実行するデータ前処理スクリプト
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #3】Processing JobとData Wranglerでデータ前処理を
#              やってみる
#
# このスクリプトは Processing Job のコンテナ内で実行される。
# 入力: /opt/ml/processing/input/raw_data.csv
# 出力: /opt/ml/processing/output/{train,validation,test}.csv
#
# 実行コンテナ: sklearn 1.2-1 イメージ
# =============================================================================

"""
SageMaker Processing Job で実行するデータ前処理スクリプト。
重複削除 → 異常値除去 → 欠損値補完 → One-Hot Encoding → スケーリング → 3分割。
"""

import pandas as pd
import numpy as np
import os
import argparse


def preprocess_data(input_path, output_path):
    """データの前処理を実行する"""

    # Step 1: データの読み込み
    print("Step 1: データの読み込み")
    df = pd.read_csv(input_path)
    print(f"  読み込みデータ: {df.shape}")

    # Step 2: 重複行の削除
    print("\nStep 2: 重複行の削除")
    before = len(df)
    df = df.drop_duplicates()
    print(f"  削除前: {before}行 → 削除後: {len(df)}行 ({before - len(df)}行削除)")

    # Step 3: 異常値の処理
    print("\nStep 3: 異常値の処理")
    # age が 0 未満または 120 超を異常値として除外
    age_outliers = ((df["age"] < 0) | (df["age"] > 120)).sum()
    df = df[(df["age"].isna()) | ((df["age"] >= 0) & (df["age"] <= 120))]
    print(f"  age異常値: {age_outliers}件を除外")

    # hours_per_week が 0 未満または 168 超を異常値として除外
    hours_outliers = ((df["hours_per_week"] < 0) | (df["hours_per_week"] > 168)).sum()
    df = df[(df["hours_per_week"].isna()) | ((df["hours_per_week"] >= 0) & (df["hours_per_week"] <= 168))]
    print(f"  hours_per_week異常値: {hours_outliers}件を除外")

    # Step 4: 欠損値の処理
    print("\nStep 4: 欠損値の処理")
    # 数値カラム: 中央値で補完
    for col in ["age", "hours_per_week", "education_num"]:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  {col}: {null_count}件をmedian({median_val})で補完")

    # カテゴリカラム: 'Unknown' で補完
    for col in ["workclass", "occupation"]:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            df[col] = df[col].fillna("Unknown")
            print(f"  {col}: {null_count}件を'Unknown'で補完")

    # Step 5: カテゴリ変数の One-Hot Encoding
    print("\nStep 5: カテゴリ変数のOne-Hot Encoding")
    categorical_cols = ["workclass", "education", "marital_status", "occupation"]
    df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    print(f"  エンコード後のカラム数: {len(df_encoded.columns)}")

    # Step 6: ターゲット変数の数値化
    print("\nStep 6: ターゲット変数の数値化")
    df_encoded["income"] = (df_encoded["income"] == ">50K").astype(int)

    # Step 7: 特徴量のスケーリング
    print("\nStep 7: 特徴量のスケーリング")
    from sklearn.preprocessing import StandardScaler

    numerical_cols = ["age", "education_num", "hours_per_week"]
    scaler = StandardScaler()
    df_encoded[numerical_cols] = scaler.fit_transform(df_encoded[numerical_cols])
    print(f"  スケーリング対象: {numerical_cols}")

    # Step 8: トレーニング / 検証 / テストデータに分割
    print("\nStep 8: データの分割")
    from sklearn.model_selection import train_test_split

    # まずトレーニング+検証とテストに分割（8:2）
    train_val, test = train_test_split(
        df_encoded, test_size=0.2, random_state=42, stratify=df_encoded["income"]
    )
    # トレーニングと検証に分割（8:2 → 全体の 6.4:1.6:2）
    train, val = train_test_split(
        train_val, test_size=0.2, random_state=42, stratify=train_val["income"]
    )

    print(f"  トレーニング: {len(train)}行")
    print(f"  検証: {len(val)}行")
    print(f"  テスト: {len(test)}行")

    # Step 9: CSV として保存
    print("\nStep 9: データの保存")
    os.makedirs(output_path, exist_ok=True)
    train.to_csv(os.path.join(output_path, "train.csv"), index=False)
    val.to_csv(os.path.join(output_path, "validation.csv"), index=False)
    test.to_csv(os.path.join(output_path, "test.csv"), index=False)
    print(f"  保存先: {output_path}")
    print("  前処理完了！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-path",
        type=str,
        default="/opt/ml/processing/input/raw_data.csv",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="/opt/ml/processing/output",
    )
    args = parser.parse_args()

    preprocess_data(args.input_path, args.output_path)
