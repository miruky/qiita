// ソース記事: AWS CDK #2 — CDKプロジェクトを作成して最初のスタックをデプロイしてみる
// S3バケット + DynamoDBテーブル + スタック出力の例

import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class MyFirstCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 バケット
    const bucket = new s3.Bucket(this, 'MyFirstBucket', {
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,        // スタック削除時にバケットも削除
      autoDeleteObjects: true,                           // バケット内オブジェクトも自動削除
    });

    // DynamoDB テーブル
    const table = new dynamodb.Table(this, 'MyFirstTable', {
      partitionKey: {
        name: 'id',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // スタック出力
    new cdk.CfnOutput(this, 'BucketName', {
      value: bucket.bucketName,
      description: 'S3 Bucket Name',
    });

    new cdk.CfnOutput(this, 'TableName', {
      value: table.tableName,
      description: 'DynamoDB Table Name',
    });
  }
}
