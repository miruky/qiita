# =============================================================================
# Amazon SageMaker #8 — SageMaker カスタムモデル + Bedrock のハイブリッド推論
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #8】SageMaker AIとBedrockを連携させて実践活用
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: XGBoost エンドポイント（deploy_realtime_endpoint.py で作成）が稼働中、
#       Bedrock Claude のモデルアクセスが有効であること
# =============================================================================

"""
SageMaker の XGBoost モデル（数値予測）と Bedrock Claude（テキスト解釈）を
組み合わせたハイブリッド推論パイプライン。

フロー:
  顧客データ → XGBoost で所得予測 → Bedrock Claude で自然言語解釈 → レポート出力
"""

import json
import boto3
import pandas as pd
import sagemaker

# ---------------------------------------------------------------------------
# 1. セットアップ
# ---------------------------------------------------------------------------

session = sagemaker.Session()
bucket = session.default_bucket()
prefix = "sagemaker-handson"
runtime_client = boto3.client("sagemaker-runtime")
bedrock_runtime = boto3.client("bedrock-runtime")

xgboost_endpoint = "xgboost-income-realtime"

# ---------------------------------------------------------------------------
# 2. テストデータの準備
# ---------------------------------------------------------------------------

test_df = pd.read_csv(f"s3://{bucket}/{prefix}/processing/output/test.csv")
sample = test_df.head(5)

target_col = "income"
feature_cols = [c for c in test_df.columns if c != target_col]

# ---------------------------------------------------------------------------
# 3. SageMaker XGBoost で予測
# ---------------------------------------------------------------------------

csv_payload = sample[feature_cols].to_csv(index=False, header=False)

response = runtime_client.invoke_endpoint(
    EndpointName=xgboost_endpoint,
    ContentType="text/csv",
    Body=csv_payload,
)

predictions = [
    float(p) for p in response["Body"].read().decode("utf-8").strip().split("\n")
]

print("XGBoost 予測結果:")
for i, pred in enumerate(predictions):
    label = "高所得（>50K）" if pred >= 0.5 else "低所得（≤50K）"
    print(f"  顧客{i+1}: {pred:.4f} → {label}")

# ---------------------------------------------------------------------------
# 4. Bedrock Claude で自然言語解釈
# ---------------------------------------------------------------------------

interpretation_prompt = f"""以下は機械学習モデル（XGBoost）による顧客の所得予測結果です。
各スコアは0〜1の確率値で、0.5以上が「高所得（>50K）」と判定されます。

予測結果:
{json.dumps([{"customer_id": i+1, "prediction_score": p, "label": "高所得" if p >= 0.5 else "低所得"} for i, p in enumerate(predictions)], ensure_ascii=False, indent=2)}

この結果をもとに、以下を日本語で分析してください:
1. 全体的な傾向
2. 高確信度の予測と低確信度の予測の区別
3. ビジネス上の推奨アクション"""

response = bedrock_runtime.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": interpretation_prompt}],
        }
    ),
)

interpretation = json.loads(response["body"].read())["content"][0]["text"]

print("\n" + "=" * 60)
print("Bedrock Claude による解釈レポート")
print("=" * 60)
print(interpretation)
