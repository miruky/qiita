// ソース記事: AWS CDK #6 — CDKのテスト・Aspects・ベストプラクティスをまとめてみる
// Aspect: S3 バケットのバージョニング必須チェック & 暗号化チェック
//
// NOTE: BucketVersioningChecker は L1（CfnBucket）の versioningConfiguration プロパティを検査します。
// L2 の s3.Bucket で versioned: true を設定すると、内部的に CfnBucket の
// versioningConfiguration.status = 'Enabled' が設定されるため、正しく動作します。

import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { IConstruct } from 'constructs';

// S3 バケットのバージョニング必須チェック
export class BucketVersioningChecker implements cdk.IAspect {
  visit(node: IConstruct): void {
    if (node instanceof s3.CfnBucket) {
      const versioning = node.versioningConfiguration as
        | s3.CfnBucket.VersioningConfigurationProperty
        | undefined;
      if (!versioning || versioning.status !== 'Enabled') {
        cdk.Annotations.of(node).addError(
          'S3 バケットにはバージョニングを有効にしてください'
        );
      }
    }
  }
}

// 暗号化必須チェック
export class EncryptionChecker implements cdk.IAspect {
  visit(node: IConstruct): void {
    if (node instanceof s3.CfnBucket) {
      if (!node.bucketEncryption) {
        cdk.Annotations.of(node).addWarning(
          'S3 バケットに暗号化が設定されていません'
        );
      }
    }
  }
}

// 使用例:
// cdk.Aspects.of(stack).add(new BucketVersioningChecker());
// cdk.Aspects.of(stack).add(new EncryptionChecker());
