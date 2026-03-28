#!/usr/bin/env node
// ソース記事: AWS CDK #4 — S3・Lambda・API GatewayでサーバーレスAPIを構築してみる
// エントリーポイント：環境（dev / prod）を Props で切り替える例

import * as cdk from 'aws-cdk-lib';
import { CdkServerlessApiStack } from '../lib/cdk-serverless-api-stack';

const app = new cdk.App();

// 開発環境
new CdkServerlessApiStack(app, 'Dev-ItemsApi', {
  env: { account: '123456789012', region: 'ap-northeast-1' },
  stageName: 'dev',
  tableDeletionProtection: false,
});

// 本番環境
new CdkServerlessApiStack(app, 'Prod-ItemsApi', {
  env: { account: '123456789012', region: 'ap-northeast-1' },
  stageName: 'prod',
  tableDeletionProtection: true,
});
