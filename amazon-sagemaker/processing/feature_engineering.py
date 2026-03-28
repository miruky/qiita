# =============================================================================
# Amazon SageMaker #3 — 特徴量エンジニアリングと重要度分析
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #3】Processing JobとData Wranglerでデータ前処理を
#              やってみる
#
# 実行環境: SageMaker Studio JupyterLab
# =============================================================================

"""
ビニング・交互作用特徴量・フラグ特徴量の作成テクニックと、
ランダムフォレストによる特徴量重要度の算出を行うスクリプト。
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# ---------------------------------------------------------------------------
# 1. 元データの読み込み
# ---------------------------------------------------------------------------

df_orig = pd.read_csv("raw_data.csv")

# ---------------------------------------------------------------------------
# 2. 特徴量エンジニアリング
# ---------------------------------------------------------------------------

# テクニック1: ビニング（年齢の区分化）
print("テクニック1: ビニング")
df_orig["age_group"] = pd.cut(
    df_orig["age"].dropna(),
    bins=[0, 25, 35, 50, 65, 120],
    labels=["Young", "Adult", "Middle", "Senior", "Elderly"],
)
print(df_orig["age_group"].value_counts())

# テクニック2: 交互作用特徴量
print("\nテクニック2: 交互作用特徴量")
df_orig["age_hours_interaction"] = df_orig["age"] * df_orig["hours_per_week"]
print(f"age × hours_per_week の統計:")
print(df_orig["age_hours_interaction"].describe())

# テクニック3: フラグ特徴量
print("\nテクニック3: フラグ特徴量")
df_orig["is_overtime"] = (df_orig["hours_per_week"] > 40).astype(int)
print(f"残業フラグの分布:")
print(df_orig["is_overtime"].value_counts())

# ---------------------------------------------------------------------------
# 3. 特徴量の重要度を簡易確認
# ---------------------------------------------------------------------------

# カテゴリ変数をラベルエンコーディング
df_temp = df_orig.dropna().copy()
le_dict = {}
for col in ["workclass", "education", "marital_status", "occupation", "age_group"]:
    le = LabelEncoder()
    df_temp[col] = le.fit_transform(df_temp[col].astype(str))
    le_dict[col] = le

df_temp["income_label"] = (df_temp["income"] == ">50K").astype(int)

# 特徴量と目的変数を設定
feature_cols = [
    "age",
    "education_num",
    "hours_per_week",
    "workclass",
    "education",
    "marital_status",
    "occupation",
    "is_overtime",
    "age_hours_interaction",
]
X = df_temp[feature_cols]
y = df_temp["income_label"]

# ランダムフォレストで特徴量の重要度を算出
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X, y)

# 重要度を表示
importance_df = pd.DataFrame(
    {"特徴量": feature_cols, "重要度": rf.feature_importances_}
).sort_values("重要度", ascending=False)

print("\n特徴量の重要度（ランダムフォレスト）")
print("=" * 40)
for _, row in importance_df.iterrows():
    bar = "█" * int(row["重要度"] * 50)
    print(f"{row['特徴量']:<25} {row['重要度']:.4f} {bar}")
