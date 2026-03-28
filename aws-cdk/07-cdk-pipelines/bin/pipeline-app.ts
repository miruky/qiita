#!/usr/bin/env node
// ソース記事: AWS CDK #7 — CDK PipelinesとCodeシリーズでCI/CDパイプラインを構築してみる
// エントリーポイント: パイプラインスタック

import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { PipelineStack } from '../lib/pipeline-stack';

const app = new cdk.App();

// パイプラインスタック（CI/CD 用アカウントにデプロイ）
new PipelineStack(app, 'PipelineStack', {
  env: {
    account: '123456789012',
    region: 'ap-northeast-1',
  },
});

app.synth();
