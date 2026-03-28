// ソース記事: AWS CDK #6 — CDKのテスト・Aspects・ベストプラクティスをまとめてみる
// Fine-Grained Assertions テスト

import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
// import { MyStack } from '../lib/my-stack'; // 実際のスタックをインポート

describe('Fine-Grained Assertions', () => {
  let template: Template;

  beforeEach(() => {
    const app = new cdk.App();
    // const stack = new MyStack(app, 'TestStack');
    // template = Template.fromStack(stack);
  });

  // --- リソースの存在確認 ---
  test('DynamoDB テーブルが作成される', () => {
    template.resourceCountIs('AWS::DynamoDB::Table', 1);
    template.resourceCountIs('AWS::Lambda::Function', 5);
    template.hasResource('AWS::S3::Bucket', {});
  });

  // --- プロパティの検証 ---
  test('DynamoDB テーブルのプロパティを検証', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      BillingMode: 'PAY_PER_REQUEST',
      KeySchema: [
        {
          AttributeName: 'id',
          KeyType: 'HASH',
        },
      ],
    });
  });

  test('S3 バケットのバージョニングを検証', () => {
    template.hasResourceProperties('AWS::S3::Bucket', {
      VersioningConfiguration: {
        Status: 'Enabled',
      },
    });
  });

  // --- Match ヘルパー ---
  test('Lambda 関数のプロパティを Match ヘルパーで検証', () => {
    // 任意の値（存在すればOK）
    template.hasResourceProperties('AWS::Lambda::Function', {
      Runtime: 'nodejs22.x',
      Handler: Match.anyValue(),
      Timeout: Match.anyValue(),
    });

    // 部分一致（他のプロパティは無視）
    template.hasResourceProperties('AWS::Lambda::Function', {
      Environment: {
        Variables: Match.objectLike({
          TABLE_NAME: Match.anyValue(),
        }),
      },
    });

    // 否定（特定の値でないことを確認）
    template.hasResourceProperties('AWS::S3::Bucket', {
      BucketName: Match.not('production-bucket'),
    });

    // 配列の部分一致
    template.hasResourceProperties('AWS::IAM::Role', {
      ManagedPolicyArns: Match.arrayWith([
        Match.stringLikeRegexp('AWSLambdaBasicExecutionRole'),
      ]),
    });
  });

  // --- Outputs の検証 ---
  test('スタック出力の検証', () => {
    template.hasOutput('ApiUrl', {
      Description: 'API Gateway URL',
    });
    template.hasOutput('TableName', {
      Value: Match.anyValue(),
    });
  });

  // --- IAM ポリシーの検証 ---
  test('Lambda に DynamoDB の読み取り権限が付与されている', () => {
    template.hasResourceProperties('AWS::IAM::Policy', {
      PolicyDocument: {
        Statement: Match.arrayWith([
          Match.objectLike({
            Action: Match.arrayWith([
              'dynamodb:GetItem',
              'dynamodb:Scan',
              'dynamodb:Query',
            ]),
            Effect: 'Allow',
          }),
        ]),
      },
    });
  });
});
