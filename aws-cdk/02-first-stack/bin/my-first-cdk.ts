#!/usr/bin/env node
// ソース記事: AWS CDK #2 — CDKプロジェクトを作成して最初のスタックをデプロイしてみる

import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { MyFirstCdkStack } from '../lib/my-first-cdk-stack';

const app = new cdk.App();
new MyFirstCdkStack(app, 'MyFirstCdkStack', {
  // env: { account: '123456789012', region: 'ap-northeast-1' },
});
