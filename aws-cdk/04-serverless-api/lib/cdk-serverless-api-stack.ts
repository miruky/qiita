// ソース記事: AWS CDK #4 — S3・Lambda・API GatewayでサーバーレスAPIを構築してみる
// サーバーレス REST API スタック定義（DynamoDB + Lambda + API Gateway）

import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as nodejs from 'aws-cdk-lib/aws-lambda-nodejs';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';
import * as path from 'path';

interface ApiStackProps extends cdk.StackProps {
  stageName: string;
  tableDeletionProtection: boolean;
}

export class CdkServerlessApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    // ========== DynamoDB ==========
    const table = new dynamodb.Table(this, 'ItemsTable', {
      partitionKey: {
        name: 'id',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: props.tableDeletionProtection
        ? cdk.RemovalPolicy.RETAIN
        : cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: true,
    });

    // ========== Lambda 共通設定 ==========
    const commonProps: Partial<nodejs.NodejsFunctionProps> = {
      runtime: lambda.Runtime.NODEJS_22_X,
      environment: {
        TABLE_NAME: table.tableName,
      },
      bundling: {
        minify: true,
        sourceMap: true,
      },
      timeout: cdk.Duration.seconds(10),
      memorySize: 256,
    };

    // ========== Lambda 関数 ==========
    const listFn = new nodejs.NodejsFunction(this, 'ListItemsFunction', {
      ...commonProps,
      entry: path.join(__dirname, '../lambda/list-items.ts'),
    });

    const createFn = new nodejs.NodejsFunction(this, 'CreateItemFunction', {
      ...commonProps,
      entry: path.join(__dirname, '../lambda/create-item.ts'),
    });

    const getFn = new nodejs.NodejsFunction(this, 'GetItemFunction', {
      ...commonProps,
      entry: path.join(__dirname, '../lambda/get-item.ts'),
    });

    const updateFn = new nodejs.NodejsFunction(this, 'UpdateItemFunction', {
      ...commonProps,
      entry: path.join(__dirname, '../lambda/update-item.ts'),
    });

    const deleteFn = new nodejs.NodejsFunction(this, 'DeleteItemFunction', {
      ...commonProps,
      entry: path.join(__dirname, '../lambda/delete-item.ts'),
    });

    // ========== IAM 権限（grant） ==========
    table.grantReadData(listFn);
    table.grantReadData(getFn);
    table.grantWriteData(createFn);
    table.grantReadWriteData(updateFn);
    table.grantWriteData(deleteFn);

    // ========== API Gateway ==========
    const api = new apigw.RestApi(this, 'ItemsApi', {
      restApiName: 'Items Service',
      description: 'CDK serverless REST API',
      deployOptions: {
        stageName: 'v1',
        throttlingRateLimit: 100,
        throttlingBurstLimit: 50,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigw.Cors.ALL_ORIGINS,
        allowMethods: apigw.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'Authorization',
          'X-Amz-Date',
          'X-Api-Key',
        ],
      },
    });

    // /items リソース
    const items = api.root.addResource('items');
    items.addMethod('GET', new apigw.LambdaIntegration(listFn));
    items.addMethod('POST', new apigw.LambdaIntegration(createFn));

    // /items/{id} リソース
    const item = items.addResource('{id}');
    item.addMethod('GET', new apigw.LambdaIntegration(getFn));
    item.addMethod('PUT', new apigw.LambdaIntegration(updateFn));
    item.addMethod('DELETE', new apigw.LambdaIntegration(deleteFn));

    // ========== 出力 ==========
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'API Gateway URL',
    });

    new cdk.CfnOutput(this, 'TableName', {
      value: table.tableName,
      description: 'DynamoDB Table Name',
    });
  }
}
