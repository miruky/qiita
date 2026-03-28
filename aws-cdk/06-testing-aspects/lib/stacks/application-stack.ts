// ソース記事: AWS CDK #6 — CDKのテスト・Aspects・ベストプラクティスをまとめてみる
// マルチスタック設計: アプリケーションスタック（別スタックの VPC を参照）

import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

interface ApplicationStackProps extends cdk.StackProps {
  vpc: ec2.Vpc;
}

export class ApplicationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ApplicationStackProps) {
    super(scope, id, props);

    // 別スタックの VPC を参照
    new lambda.Function(this, 'MyFunction', {
      vpc: props.vpc,
      runtime: lambda.Runtime.NODEJS_22_X,
      handler: 'index.handler',
      code: lambda.Code.fromInline('exports.handler = async () => {}'),
    });
  }
}
