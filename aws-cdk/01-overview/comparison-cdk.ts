// ソース記事: AWS CDK #1 — CDKって何？CloudFormation・SAMとの違いを整理してみる
// S3バケット + Lambda関数 + API Gateway を CDK で定義する例

import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';

export class MyStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string) {
    super(scope, id);

    const bucket = new s3.Bucket(this, 'MyBucket', {
      versioned: true,
    });

    const fn = new lambda.Function(this, 'MyHandler', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
def handler(event, context):
    return {'statusCode': 200, 'body': 'Hello'}
      `),
    });

    new apigw.LambdaRestApi(this, 'MyApi', {
      handler: fn,
    });
  }
}
