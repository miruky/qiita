# =============================================================================
# Amazon SageMaker #8 — Processing Job 内で Bedrock を呼び出すスクリプト
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #8】SageMaker AIとBedrockを連携させて実践活用
#              してみる
#
# このスクリプトは Processing Job のコンテナ内で実行される。
# 入力: /opt/ml/processing/input/reviews.csv
# 出力: /opt/ml/processing/output/analyzed_reviews.csv
#
# 注意: Processing Job の実行ロールに bedrock:InvokeModel 権限が必要。
# =============================================================================

"""
SageMaker Processing Job のコンテナ内から Bedrock Claude を呼び出し、
レビューの感情分析を一括実行する。
"""

import json
import os
import time
import argparse

import boto3
import pandas as pd


def analyze_with_bedrock(review_text, bedrock_runtime):
    """Bedrock Claude でレビューを分析する"""
    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 256,
                    "messages": [
                        {
                            "role": "user",
                            "content": f"以下のレビューの感情をpositive/negative/neutralで判定し、"
                            f"理由を1文で述べてください。JSON形式で出力。\n\nレビュー: {review_text}",
                        }
                    ],
                }
            ),
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
    except Exception as e:
        return json.dumps({"sentiment": "error", "reason": str(e)})


def main(input_path, output_path):
    """メイン処理"""
    bedrock_runtime = boto3.client("bedrock-runtime")

    # データの読み込み
    print(f"入力データ: {input_path}")
    df = pd.read_csv(input_path)
    print(f"レビュー数: {len(df)}")

    # Bedrock で分析
    results = []
    for i, row in df.iterrows():
        print(f"分析中: {i+1}/{len(df)}")
        analysis = analyze_with_bedrock(row["review"], bedrock_runtime)
        results.append(analysis)
        time.sleep(0.5)  # レート制限対策

    df["bedrock_analysis"] = results

    # 結果の保存
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "analyzed_reviews.csv")
    df.to_csv(output_file, index=False)
    print(f"分析結果を保存: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-path",
        type=str,
        default="/opt/ml/processing/input/reviews.csv",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="/opt/ml/processing/output",
    )
    args = parser.parse_args()

    main(args.input_path, args.output_path)
