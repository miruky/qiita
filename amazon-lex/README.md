# Amazon Lex（Qiita 連載シリーズ）

Qiita 連載「Amazon Lex」シリーズ（全6回）のコードをまとめたディレクトリです。

## 概要

Amazon Lex V2 を使ったチャットボット構築の全工程を扱います。
ボットの基本設計から Lambda 連携、Amazon Connect 統合、音声認識精度の向上テクニックまでを一通りカバーしています。

## ファイル一覧

| ファイル | 記事 | 説明 |
|:--|:--|:--|
| lambda/order_lookup.py | #3 | 注文確認ボット用 Lambda 関数（ダイアログ＋フルフィルメント） |
| lambda/order_lookup_error_handling.py | #3 | try-except によるエラーハンドリングを追加した改良版 |
| lambda/confidence_score_handler.py | #5 | NLU / ASR 信頼度スコアに基づくバリデーション |
| lambda/runtime_hints_handler.py | #6 | Runtime Hints API で動的に音声認識ヒントを設定 |
| lambda/session_attributes_handler.py | #6 | Connect セッション属性 + Runtime Hints でパーソナライズ |
| config/custom-vocabulary.tsv | #5 | カスタムボキャブラリー定義ファイル（ヘッダなし） |
| config/ssml-examples.xml | #4 / #6 | SSML による音声合成制御のサンプル |

## 関連記事

- #1 — Lexって何？会話型AIサービスの全体像をつかんでみる
- #2 — はじめてのLexボットでインテント・スロット・発話を設計してみる
- #3 — Lambda連携で動的な応答を返せるようにしてみる
- #4 — Amazon ConnectとLexを統合して音声ボットを構築してみる
- #5 — Lexの音声認識精度を高めるテクニックを試してみる
- #6 — Amazon Connectを活用してLexの文字起こし精度を向上させてみる
