// ソース記事: AWS CDK #5 — DynamoDB・SQS・SNSでイベント駆動アーキテクチャを作ってみる
// イベント駆動アーキテクチャ: DynamoDB Streams, SNS, SQS, EventBridge, Step Functions

import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as nodejs from 'aws-cdk-lib/aws-lambda-nodejs';
import * as eventsources from 'aws-cdk-lib/aws-lambda-event-sources';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import { Construct } from 'constructs';
import * as path from 'path';

export class EventDrivenStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ==========================================================
    // DynamoDB テーブル（Streams有効）
    // ==========================================================
    const ordersTable = new dynamodb.Table(this, 'OrdersTable', {
      partitionKey: {
        name: 'orderId',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // ==========================================================
    // SNS トピック（イベントファンアウト）
    // ==========================================================
    const orderEventsTopic = new sns.Topic(this, 'OrderEventsTopic', {
      topicName: 'order-events',
      displayName: '注文イベント',
    });

    // ==========================================================
    // SQS キュー（DLQ付き）
    // ==========================================================
    const inventoryDlq = new sqs.Queue(this, 'InventoryDLQ', {
      queueName: 'inventory-dlq',
      retentionPeriod: cdk.Duration.days(14),
    });

    const inventoryQueue = new sqs.Queue(this, 'InventoryQueue', {
      queueName: 'inventory-queue',
      visibilityTimeout: cdk.Duration.seconds(60),
      deadLetterQueue: {
        queue: inventoryDlq,
        maxReceiveCount: 3,
      },
    });

    const shippingQueue = new sqs.Queue(this, 'ShippingQueue', {
      queueName: 'shipping-queue',
      visibilityTimeout: cdk.Duration.seconds(60),
    });

    const analyticsQueue = new sqs.Queue(this, 'AnalyticsQueue', {
      queueName: 'analytics-queue',
      visibilityTimeout: cdk.Duration.seconds(60),
    });

    // ==========================================================
    // SNS → SQS サブスクリプション（ファンアウト）
    // ==========================================================
    orderEventsTopic.addSubscription(
      new subscriptions.SqsSubscription(inventoryQueue)
    );
    orderEventsTopic.addSubscription(
      new subscriptions.SqsSubscription(shippingQueue)
    );
    orderEventsTopic.addSubscription(
      new subscriptions.SqsSubscription(analyticsQueue)
    );

    // ==========================================================
    // DynamoDB Streams → Lambda（Stream Processor）
    // ==========================================================
    const streamProcessor = new nodejs.NodejsFunction(this, 'StreamProcessor', {
      entry: path.join(__dirname, '../lambda/stream-processor.ts'),
      runtime: lambda.Runtime.NODEJS_22_X,
      timeout: cdk.Duration.seconds(30),
    });

    streamProcessor.addEventSource(
      new eventsources.DynamoEventSource(ordersTable, {
        startingPosition: lambda.StartingPosition.TRIM_HORIZON,
        batchSize: 10,
        maxBatchingWindow: cdk.Duration.seconds(5),
        retryAttempts: 3,
      })
    );

    // Lambda に SNS Publish 権限を付与
    orderEventsTopic.grantPublish(streamProcessor);
    streamProcessor.addEnvironment('TOPIC_ARN', orderEventsTopic.topicArn);

    // ==========================================================
    // SQS → Lambda（各処理系）
    // ==========================================================
    const inventoryUpdater = new nodejs.NodejsFunction(this, 'InventoryUpdater', {
      entry: path.join(__dirname, '../lambda/inventory-updater.ts'),
      runtime: lambda.Runtime.NODEJS_22_X,
      timeout: cdk.Duration.seconds(30),
    });
    inventoryUpdater.addEventSource(
      new eventsources.SqsEventSource(inventoryQueue, {
        batchSize: 10,
        maxBatchingWindow: cdk.Duration.seconds(5),
        reportBatchItemFailures: true,
      })
    );

    // ==========================================================
    // EventBridge スケジュール実行
    // ==========================================================
    const dailyReportFn = new nodejs.NodejsFunction(this, 'DailyReport', {
      entry: path.join(__dirname, '../lambda/daily-report.ts'),
      runtime: lambda.Runtime.NODEJS_22_X,
      timeout: cdk.Duration.minutes(5),
    });

    // 毎日 AM 9:00（JST = UTC 0:00）に実行
    new events.Rule(this, 'DailyReportRule', {
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '0',
      }),
      targets: [new targets.LambdaFunction(dailyReportFn)],
    });

    // ==========================================================
    // DLQ アラーム
    // ==========================================================
    inventoryDlq.metricApproximateNumberOfMessagesVisible()
      .createAlarm(this, 'DLQAlarm', {
        alarmName: 'DLQ-Messages-Alarm',
        threshold: 1,
        evaluationPeriods: 1,
      });
  }
}
