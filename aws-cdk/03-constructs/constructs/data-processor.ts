// ソース記事: AWS CDK #3 — L1・L2・L3コンストラクトを使い分けてみる
// カスタムコンストラクトの作成例：S3 + Lambda のデータ処理パターン

import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

// Props インターフェース
export interface DataProcessorProps {
  readonly bucketName?: string;
  readonly retentionDays?: number;
}

// カスタムコンストラクト
export class DataProcessor extends Construct {
  public readonly bucket: s3.Bucket;
  public readonly processorFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: DataProcessorProps = {}) {
    super(scope, id);

    // S3 バケット
    this.bucket = new s3.Bucket(this, 'DataBucket', {
      bucketName: props.bucketName,
      versioned: true,
      lifecycleRules: [
        {
          expiration: cdk.Duration.days(props.retentionDays ?? 90),
        },
      ],
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    // Lambda 関数
    this.processorFunction = new lambda.Function(this, 'Processor', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
import json
def handler(event, context):
    print(json.dumps(event))
    return {'statusCode': 200}
      `),
      environment: {
        BUCKET_NAME: this.bucket.bucketName,
      },
    });

    // S3 → Lambda への読み取り権限
    this.bucket.grantRead(this.processorFunction);
  }
}
