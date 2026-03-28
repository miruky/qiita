// ソース記事: AWS CDK #3 — L1・L2・L3コンストラクトを使い分けてみる
// エスケープハッチ：L2 → L1 に降りてプロパティを直接制御する例

import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export class EscapeHatchExampleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // =============================================
    // L2 → L1 への降格でプロパティを直接設定
    // =============================================
    const bucket = new s3.Bucket(this, 'MyBucket', {
      versioned: true,
    });

    // L2 → L1 に降りて、L2で設定できないプロパティを直接設定
    const cfnBucket = bucket.node.defaultChild as s3.CfnBucket;

    // CloudFormation プロパティを直接操作
    cfnBucket.accelerateConfiguration = {
      accelerationStatus: 'Enabled',
    };

    cfnBucket.analyticsConfigurations = [
      {
        id: 'full-analysis',
        storageClassAnalysis: {
          dataExport: {
            destination: {
              bucketArn: 'arn:aws:s3:::analytics-dest-bucket',
              format: 'CSV',
            },
            outputSchemaVersion: 'V_1',
          },
        },
      },
    ];

    // =============================================
    // プロパティの上書き（addPropertyOverride）
    // =============================================
    const fn = new lambda.Function(this, 'MyFunction', {
      runtime: lambda.Runtime.NODEJS_22_X,
      handler: 'index.handler',
      code: lambda.Code.fromInline('exports.handler = async () => ({statusCode:200})'),
    });

    const cfnFunction = fn.node.defaultChild as lambda.CfnFunction;

    // L2で公開されていない、または最新のCFnプロパティを直接設定
    cfnFunction.addPropertyOverride('LoggingConfig', {
      LogFormat: 'JSON',
      SystemLogLevel: 'WARN',
    });

    // 特定のプロパティを削除
    cfnFunction.addPropertyDeletionOverride('Environment');
  }
}
