// ソース記事: AWS CDK #7 — CDK PipelinesとCodeシリーズでCI/CDパイプラインを構築してみる
// CDK Pipelines: セルフミューテーティングパイプライン + 3ステージ（Dev/Stg/Prod）

import * as cdk from 'aws-cdk-lib';
import * as pipelines from 'aws-cdk-lib/pipelines';
import { Construct } from 'constructs';
import { ApplicationStage } from './application-stage';

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // パイプラインの定義
    const pipeline = new pipelines.CodePipeline(this, 'Pipeline', {
      pipelineName: 'MyAppPipeline',
      synth: new pipelines.ShellStep('Synth', {
        // ソース：GitHub リポジトリ
        input: pipelines.CodePipelineSource.connection(
          'myorg/my-cdk-app',     // GitHub リポジトリ
          'main',                  // ブランチ
          {
            connectionArn: 'arn:aws:codestar-connections:ap-northeast-1:123456789012:connection/xxxx',
          }
        ),
        // ビルドコマンド
        commands: [
          'npm ci',
          'npm run build',
          'npm run test',
          'npx cdk synth',
        ],
      }),
      // Docker を使う場合（Lambda コンテナ等）
      dockerEnabledForSynth: true,
    });

    // ===== Dev ステージ =====
    pipeline.addStage(new ApplicationStage(this, 'Dev', {
      stageName: 'dev',
      env: { account: '123456789012', region: 'ap-northeast-1' },
    }), {
      pre: [
        // デプロイ前にセキュリティチェック
        new pipelines.ShellStep('SecurityCheck', {
          commands: [
            'npm ci',
            'npm run audit',
            'npx cdk diff',
          ],
        }),
      ],
    });

    // ===== Staging ステージ =====
    pipeline.addStage(new ApplicationStage(this, 'Staging', {
      stageName: 'stg',
      env: { account: '123456789012', region: 'ap-northeast-1' },
    }), {
      post: [
        // デプロイ後に統合テスト
        new pipelines.ShellStep('IntegrationTest', {
          commands: [
            'npm ci',
            'npm run test:integration',
          ],
        }),
      ],
    });

    // ===== Production ステージ（手動承認付き） =====
    pipeline.addStage(new ApplicationStage(this, 'Production', {
      stageName: 'prod',
      env: { account: '123456789012', region: 'ap-northeast-1' },
    }), {
      pre: [
        new pipelines.ManualApprovalStep('PromoteToProd', {
          comment: '本番環境にデプロイしますか？Staging の動作確認が完了していることを確認してください。',
        }),
      ],
    });
  }
}

// NOTE: クロスアカウントデプロイ時の bootstrap コマンド:
//   cdk bootstrap aws://999888777666/ap-northeast-1 \
//     --trust 123456789012 \
//     --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess
//
// WARNING: AdministratorAccess はすべての操作を許可するため、本番環境では
// より制限的なポリシー（例：PowerUserAccess や組織固有のカスタムポリシー）を
// 使用することを強く推奨します。
