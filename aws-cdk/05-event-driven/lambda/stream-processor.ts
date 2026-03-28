// ソース記事: AWS CDK #5 — DynamoDB・SQS・SNSでイベント駆動アーキテクチャを作ってみる
// DynamoDB Streams を処理する Lambda ハンドラー

import { DynamoDBStreamEvent } from 'aws-lambda';

export const handler = async (event: DynamoDBStreamEvent) => {
  for (const record of event.Records) {
    console.log('EventName:', record.eventName);
    console.log('NewImage:', JSON.stringify(record.dynamodb?.NewImage));

    if (record.eventName === 'INSERT') {
      // 新規注文 → SNS に通知
      console.log('新規注文を検知しました');
    }
  }
};
