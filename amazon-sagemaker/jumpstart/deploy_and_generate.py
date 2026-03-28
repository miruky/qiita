# =============================================================================
# Amazon SageMaker #7 — JumpStart で Llama 3.1 をデプロイしてテキスト生成
# =============================================================================
# Qiita 記事: 【Amazon SageMaker #7】JumpStartで基盤モデルをサクッと活用してみる
#
# 実行環境: SageMaker Studio JupyterLab
# 注意: Llama 3.1 8B のデプロイには ml.g5.2xlarge（GPU）が必要。
#       無料利用枠外のためコスト注意。
# =============================================================================

"""
JumpStart から Llama 3.1 8B Instruct をデプロイし、
さまざまなユースケースでテキスト生成を行う。
"""

import json
import sagemaker
from sagemaker.jumpstart.model import JumpStartModel

# ---------------------------------------------------------------------------
# 1. モデルの検索
# ---------------------------------------------------------------------------

from sagemaker.jumpstart.notebook_utils import list_jumpstart_models

text_gen_models = list_jumpstart_models(filter_value="task == txt2txt")
llama_models = [m for m in text_gen_models if "llama" in m.lower()]

print("Llama 関連モデル:")
for m in llama_models[:10]:
    print(f"  - {m}")

# ---------------------------------------------------------------------------
# 2. Llama 3.1 8B Instruct のデプロイ
# ---------------------------------------------------------------------------

model_id = "meta-textgeneration-llama-3-1-8b-instruct"

model = JumpStartModel(
    model_id=model_id,
    role=sagemaker.get_execution_role(),
)

print(f"\nモデル '{model_id}' をデプロイ中...")
print("（5〜10分ほどかかります）")

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.2xlarge",
    accept_eula=True,  # Llama のライセンス同意が必要
)

endpoint_name = predictor.endpoint_name
print(f"デプロイ完了！ エンドポイント: {endpoint_name}")

# ---------------------------------------------------------------------------
# 3. テキスト生成ヘルパー
# ---------------------------------------------------------------------------

def generate_text(predictor, prompt, max_tokens=512, temperature=0.6, top_p=0.9):
    """テキスト生成のヘルパー関数"""
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": True,
        },
    }
    response = predictor.predict(payload)
    # レスポンス形式はモデルにより異なる
    if isinstance(response, list):
        return response[0].get("generated_text", str(response))
    return str(response)

# ---------------------------------------------------------------------------
# 4. ユースケース別のテキスト生成
# ---------------------------------------------------------------------------

# ユースケース 1: コード生成
print("=" * 50)
print("ユースケース1: コード生成")
print("=" * 50)
code_prompt = """<|begin_of_text|><|start_header_id|>user<|end_header_id|>
PythonでFizzBuzzを実装してください。1から100まで出力してください。
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

result = generate_text(predictor, code_prompt)
print(result)

# ユースケース 2: テキスト要約
print("\n" + "=" * 50)
print("ユースケース2: テキスト要約")
print("=" * 50)
summary_prompt = """<|begin_of_text|><|start_header_id|>user<|end_header_id|>
以下のテキストを3行で要約してください。

Amazon SageMaker AIは、機械学習モデルの構築、トレーニング、デプロイを
支援するフルマネージドサービスです。データサイエンティストや開発者が
機械学習ワークフロー全体を効率的に管理できるように設計されています。
JupyterLabベースの統合開発環境、分散トレーニング、自動モデルチューニング、
複数の推論オプションなど、豊富な機能を提供しています。

<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

result = generate_text(predictor, summary_prompt, max_tokens=256)
print(result)

# ユースケース 3: 質問応答
print("\n" + "=" * 50)
print("ユースケース3: 質問応答")
print("=" * 50)
qa_prompt = """<|begin_of_text|><|start_header_id|>user<|end_header_id|>
AWSのリージョンとアベイラビリティゾーンの違いを簡潔に説明してください。
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

result = generate_text(predictor, qa_prompt, max_tokens=256)
print(result)

# ---------------------------------------------------------------------------
# 5. クリーンアップ
# ---------------------------------------------------------------------------

# predictor.delete_endpoint()
# print("エンドポイントを削除しました。")
