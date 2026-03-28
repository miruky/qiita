// ソース記事: AWS CDK #3 — L1・L2・L3コンストラクトを使い分けてみる
// L1 コンストラクト（CfnBucket）の例

import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class L1ExampleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // L1: CloudFormation の AWS::S3::Bucket と完全対応
    new s3.CfnBucket(this, 'MyL1Bucket', {
      bucketName: 'my-l1-bucket-example',
      versioningConfiguration: {
        status: 'Enabled',
      },
      bucketEncryption: {
        serverSideEncryptionConfiguration: [
          {
            serverSideEncryptionByDefault: {
              sseAlgorithm: 'AES256',
            },
          },
        ],
      },
      publicAccessBlockConfiguration: {
        blockPublicAcls: true,
        blockPublicPolicy: true,
        ignorePublicAcls: true,
        restrictPublicBuckets: true,
      },
    });
  }
}
