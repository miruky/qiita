// ソース記事: AWS CDK #6 — CDKのテスト・Aspects・ベストプラクティスをまとめてみる
// Aspects のテスト

import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Annotations, Match } from 'aws-cdk-lib/assertions';
import { BucketVersioningChecker } from '../lib/aspects/bucket-versioning-checker';

test('バージョニング未設定のバケットでエラーが出る', () => {
  const app = new cdk.App();
  const stack = new cdk.Stack(app, 'TestStack');

  // バージョニング未設定のバケット
  new s3.Bucket(stack, 'BadBucket');

  // Aspect を適用
  cdk.Aspects.of(stack).add(new BucketVersioningChecker());

  // synth してアノテーションを検証
  const annotations = Annotations.fromStack(stack);
  annotations.hasError(
    '/TestStack/BadBucket/Resource',
    Match.stringLikeRegexp('バージョニング')
  );
});
