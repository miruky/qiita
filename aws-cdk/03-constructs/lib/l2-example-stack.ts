// ソース記事: AWS CDK #3 — L1・L2・L3コンストラクトを使い分けてみる
// L2 コンストラクト（Bucket）の例 + L1 vs L2 の Lambda 定義比較

import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class L2ExampleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // =============================================
    // L2: 高レベル抽象化。暗号化やパブリックアクセスブロックはデフォルトで有効
    // =============================================
    const bucket = new s3.Bucket(this, 'MyL2Bucket', {
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // L2ならではの便利メソッド
    bucket.addLifecycleRule({
      expiration: cdk.Duration.days(90),
      transitions: [
        {
          storageClass: s3.StorageClass.GLACIER,
          transitionAfter: cdk.Duration.days(30),
        },
      ],
    });

    bucket.addCorsRule({
      allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.PUT],
      allowedOrigins: ['https://example.com'],
      allowedHeaders: ['*'],
    });

    // =============================================
    // L1 で Lambda 関数を定義（比較用）
    // =============================================
    const role = new iam.CfnRole(this, 'FnRole', {
      assumeRolePolicyDocument: {
        Version: '2012-10-17',
        Statement: [{
          Effect: 'Allow',
          Principal: { Service: 'lambda.amazonaws.com' },
          Action: 'sts:AssumeRole',
        }],
      },
      managedPolicyArns: [
        'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
      ],
    });

    new lambda.CfnFunction(this, 'FnL1', {
      functionName: 'my-handler',
      runtime: 'python3.13',
      handler: 'index.handler',
      role: role.attrArn,
      code: { zipFile: 'def handler(event, context): return {"statusCode": 200}' },
    });

    // =============================================
    // L2 で Lambda 関数を定義（IAMロール・ログ出力権限は自動生成）
    // =============================================
    new lambda.Function(this, 'FnL2', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'index.handler',
      code: lambda.Code.fromInline(
        'def handler(event, context): return {"statusCode": 200}'
      ),
    });
  }
}
