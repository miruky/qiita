# =============================================================================
# Amazon SageMaker #8 — SageMaker で前処理 → Bedrock Claude で分析
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #8】SageMaker AIとBedrockを連携させて実践活用
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: Bedrock で Claude 3.5 Sonnet のモデルアクセスが有効であること
# =============================================================================

"""
SageMaker で商品レビューデータの前処理を行い、
Bedrock Claude でテキスト分析（感情・要約・カテゴリ分類）を実行する。
"""

import json
import time
import pandas as pd
import numpy as np
import sagemaker
import boto3

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson/bedrock-integration"
role = sagemaker.get_execution_role()
bedrock_runtime = boto3.client("bedrock-runtime")

print(f"バケット: {bucket}")
print(f"ロール: {role}")

# ---------------------------------------------------------------------------
# 2. 商品レビューデータの作成
# ---------------------------------------------------------------------------

np.random.seed(42)

reviews = [
    {"product": "ワイヤレスイヤホン", "review": "音質が素晴らしく、ノイズキャンセリングも効果的です。バッテリーの持ちも良く、毎日の通勤で使っています。", "rating": 5},
    {"product": "ワイヤレスイヤホン", "review": "接続が頻繁に切れます。価格の割に品質が低いと感じました。", "rating": 2},
    {"product": "スマートウォッチ", "review": "健康管理機能が充実していて、睡眠トラッキングが特に正確です。", "rating": 4},
    {"product": "スマートウォッチ", "review": "画面が小さくて見づらいです。アプリの動作も遅く、ストレスを感じます。", "rating": 1},
    {"product": "モバイルバッテリー", "review": "軽量で持ち運びやすく、充電速度も十分です。デザインもシンプルで気に入っています。", "rating": 5},
    {"product": "モバイルバッテリー", "review": "容量表示と実際の容量に差があるように感じます。2回目のフル充電ができません。", "rating": 2},
    {"product": "Bluetoothスピーカー", "review": "コンパクトなのに迫力のある音が出ます。防水機能もあってキャンプで重宝しています。", "rating": 5},
    {"product": "Bluetoothスピーカー", "review": "低音が強すぎてバランスが悪いです。イコライザー設定もできず残念。", "rating": 3},
]

df = pd.DataFrame(reviews)
print(f"レビューデータ: {df.shape}")
print(df.head())

# ---------------------------------------------------------------------------
# 3. 前処理
# ---------------------------------------------------------------------------

df["review_length"] = df["review"].str.len()
df["word_count"] = df["review"].str.split().str.len()
df["sentiment_label"] = df["rating"].apply(
    lambda x: "positive" if x >= 4 else ("negative" if x <= 2 else "neutral")
)

print("\n前処理後のデータ:")
print(df[["product", "rating", "sentiment_label", "review_length"]].to_string())

# S3 にアップロード
df.to_csv(f"s3://{bucket}/{prefix}/reviews/processed_reviews.csv", index=False)
print(f"\nS3にアップロード完了: s3://{bucket}/{prefix}/reviews/")

# ---------------------------------------------------------------------------
# 4. Bedrock Claude によるレビュー分析
# ---------------------------------------------------------------------------

def analyze_review(review_text, product_name):
    """Bedrock Claude でレビューを分析する"""
    prompt = f"""以下の商品レビューを分析し、JSON形式で結果を返してください。

商品名: {product_name}
レビュー: {review_text}

分析項目:
1. sentiment: positive/negative/neutral
2. key_points: 主要ポイント（リスト形式）
3. improvement_suggestions: 改善提案（あれば）
4. category: 品質/機能/デザイン/価格/サービス

JSON形式で出力:"""

    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            }
        ),
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


# 全レビューを分析
print("\nBedrock Claude によるレビュー分析:")
print("=" * 60)

analysis_results = []
for _, row in df.iterrows():
    print(f"\n[{row['product']}] 評価: {row['rating']}★")
    print(f"レビュー: {row['review'][:50]}...")

    analysis = analyze_review(row["review"], row["product"])
    print(f"分析結果: {analysis}")
    analysis_results.append(analysis)

    time.sleep(1)  # レート制限対策

df["ai_analysis"] = analysis_results

# ---------------------------------------------------------------------------
# 5. レポート生成
# ---------------------------------------------------------------------------

report_prompt = f"""以下の商品レビュー分析結果をもとに、経営判断に役立つレポートを作成してください。

データ概要:
- 総レビュー数: {len(df)}
- 商品カテゴリ: {df['product'].nunique()}種類
- 平均評価: {df['rating'].mean():.1f}
- 高評価（4以上）の割合: {(df['rating'] >= 4).mean()*100:.0f}%

商品別の平均評価:
{df.groupby('product')['rating'].mean().to_string()}

分析結果サマリーを日本語で作成してください。"""

response = bedrock_runtime.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": report_prompt}],
        }
    ),
)

report = json.loads(response["body"].read())["content"][0]["text"]
print("\n" + "=" * 60)
print("経営レポート")
print("=" * 60)
print(report)
