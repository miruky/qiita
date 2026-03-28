# =============================================================================
# Amazon SageMaker #8 — Bedrock Titan Embeddings でベクトル検索
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #8】SageMaker AIとBedrockを連携させて実践活用
#              してみる
#
# 実行環境: SageMaker Studio JupyterLab
# 前提: Bedrock で Amazon Titan Embeddings V2 のモデルアクセスが有効であること
# =============================================================================

"""
Bedrock Titan Embeddings でテキストをベクトル化し、
コサイン類似度による類似製品レビューの検索を実現する。
"""

import json
import numpy as np
import boto3

bedrock_runtime = boto3.client("bedrock-runtime")

# ---------------------------------------------------------------------------
# 1. テキストのベクトル化関数
# ---------------------------------------------------------------------------

def get_embedding(text):
    """Bedrock Titan Embeddings V2 でテキストをベクトル化する"""
    response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text}),
    )
    result = json.loads(response["body"].read())
    return result["embedding"]


def cosine_similarity(vec1, vec2):
    """コサイン類似度を計算する"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# ---------------------------------------------------------------------------
# 2. 製品ドキュメントのベクトル化
# ---------------------------------------------------------------------------

documents = [
    "ワイヤレスイヤホンの音質は業界最高水準。ノイズキャンセリング機能搭載。",
    "スマートウォッチは24時間の健康モニタリングに対応。GPS内蔵。",
    "モバイルバッテリーは20000mAhの大容量。USB-C急速充電対応。",
    "Bluetoothスピーカーは防水IPX7対応。360度サウンド。",
    "ワイヤレス充電パッドはQi規格対応。最大15W出力。",
]

print("ドキュメントのベクトル化中...")
doc_embeddings = []
for doc in documents:
    embedding = get_embedding(doc)
    doc_embeddings.append(embedding)
    print(f"  ベクトル化完了: {doc[:30]}... (次元数: {len(embedding)})")

# ---------------------------------------------------------------------------
# 3. 類似ドキュメントの検索
# ---------------------------------------------------------------------------

query = "防水で音楽が聴けるデバイスが欲しい"
query_embedding = get_embedding(query)

print(f"\nクエリ: 「{query}」")
print("\n検索結果（類似度順）:")
print("-" * 60)

similarities = []
for i, (doc, doc_emb) in enumerate(zip(documents, doc_embeddings)):
    sim = cosine_similarity(query_embedding, doc_emb)
    similarities.append((sim, doc))

similarities.sort(reverse=True)
for rank, (sim, doc) in enumerate(similarities, 1):
    print(f"  {rank}. [{sim:.4f}] {doc}")

# ---------------------------------------------------------------------------
# 4. 別のクエリでも試す
# ---------------------------------------------------------------------------

queries = [
    "バッテリーが長持ちする充電器",
    "健康管理に便利なウェアラブルデバイス",
    "音楽を高音質で楽しみたい",
]

for query in queries:
    query_emb = get_embedding(query)
    print(f"\nクエリ: 「{query}」")

    best_sim = -1
    best_doc = ""
    for doc, doc_emb in zip(documents, doc_embeddings):
        sim = cosine_similarity(query_emb, doc_emb)
        if sim > best_sim:
            best_sim = sim
            best_doc = doc

    print(f"  最も関連: [{best_sim:.4f}] {best_doc}")
