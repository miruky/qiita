// ソース記事: AWS CDK #3 — L1・L2・L3コンストラクトを使い分けてみる
// L3 コンストラクト（LambdaRestApi）の例

import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';

export class L3ExampleStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const fn = new lambda.Function(this, 'Handler', {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: 'index.handler',
      code: lambda.Code.fromInline(`
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from CDK!'
    }
      `),
    });

    // L3: Lambda + API Gateway + IAM + Deployment + Stage を一発で構築
    const api = new apigw.LambdaRestApi(this, 'MyApi', {
      handler: fn,
      proxy: true,  // すべてのリクエストをLambdaにルーティング
    });

    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
    });
  }
}
