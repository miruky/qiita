// ソース記事: AWS CDK #7 — CDK PipelinesとCodeシリーズでCI/CDパイプラインを構築してみる
// アプリケーションステージ: 複数のスタック（Database + API）をまとめたデプロイ単位

import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import { ApiStack } from './stacks/api-stack';
// import { DatabaseStack } from './stacks/database-stack';

export interface ApplicationStageProps extends cdk.StageProps {
  stageName: string;
}

export class ApplicationStage extends cdk.Stage {
  public readonly apiUrl: cdk.CfnOutput;

  constructor(scope: Construct, id: string, props: ApplicationStageProps) {
    super(scope, id, props);

    // データベーススタック
    // const dbStack = new DatabaseStack(this, 'Database', {
    //   stageName: props.stageName,
    // });

    // API スタック
    // const apiStack = new ApiStack(this, 'Api', {
    //   stageName: props.stageName,
    //   table: dbStack.table,
    // });

    // this.apiUrl = apiStack.apiUrl;
  }
}
