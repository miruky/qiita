"""
AWS SDK (Boto3) シリーズ #5
イベント駆動パターン：SNS → SQS / SQS → Lambda / S3 → Lambda
"""

import json

import boto3


# ---------------------------------------------------------------------------
# パターン1：SNS → SQS（ファンアウト）
# ---------------------------------------------------------------------------

def sns_to_sqs_fanout():
    """1 回の Publish で複数の SQS キューにメッセージを配信する"""
    sns = boto3.client('sns')
    sqs = boto3.client('sqs')

    topic_arn = 'arn:aws:sns:ap-northeast-1:123456789012:order-events'

    # 複数の SQS キューにファンアウト
    queues = {
        'inventory-queue': '在庫管理',
        'shipping-queue': '配送処理',
        'analytics-queue': '分析',
    }

    for queue_name, description in queues.items():
        # キュー作成
        q = sqs.create_queue(QueueName=queue_name)

        # キューの ARN を取得
        attrs = sqs.get_queue_attributes(
            QueueUrl=q['QueueUrl'],
            AttributeNames=['QueueArn']
        )

        # SNS トピックにサブスクライブ
        sns.subscribe(
            TopicArn=topic_arn,
            Protocol='sqs',
            Endpoint=attrs['Attributes']['QueueArn']
        )
        print(f"  {description}キューをサブスクライブしました")

    # 1 回の Publish で全キューにメッセージが届く
    sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps({
            'order_id': 'ord-001',
            'customer': 'c001',
            'total': 15000
        })
    )
    print("注文イベントを発行しました")


# ---------------------------------------------------------------------------
# パターン2：SQS → Lambda（ポーリング処理）
# ---------------------------------------------------------------------------

def sqs_to_lambda_polling():
    """SQS からメッセージを受信して Lambda に渡す（手動ポーリング例）

    NOTE: 実運用では SQS をイベントソースマッピングとして Lambda に設定し、
    AWS が自動でポーリング→Lambda 呼び出しを行うのが一般的です。
    """
    sqs = boto3.client('sqs')
    lambda_client = boto3.client('lambda')

    queue_url = (
        'https://sqs.ap-northeast-1.amazonaws.com/123456789012/my-task-queue'
    )

    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=20
        )

        messages = response.get('Messages', [])
        if not messages:
            continue

        for msg in messages:
            # Lambda を同期呼び出し
            result = lambda_client.invoke(
                FunctionName='process-task',
                InvocationType='RequestResponse',
                Payload=msg['Body']
            )

            status = result['StatusCode']
            if status == 200:
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=msg['ReceiptHandle']
                )
                print(f"処理完了: {msg['MessageId']}")
            else:
                print(f"処理失敗: {msg['MessageId']}")


# ---------------------------------------------------------------------------
# パターン3：S3 イベント → Lambda
# ---------------------------------------------------------------------------

def s3_to_lambda_trigger():
    """S3 のオブジェクト作成イベントで Lambda を起動する"""
    s3 = boto3.client('s3')
    lambda_client = boto3.client('lambda')

    # Lambda 関数に S3 からの呼び出し権限を追加
    lambda_client.add_permission(
        FunctionName='image-processor',
        StatementId='s3-trigger',
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn='arn:aws:s3:::my-image-bucket'
    )

    # S3 バケットにイベント通知を設定
    s3.put_bucket_notification_configuration(
        Bucket='my-image-bucket',
        NotificationConfiguration={
            'LambdaFunctionConfigurations': [
                {
                    'LambdaFunctionArn': (
                        'arn:aws:lambda:ap-northeast-1:123456789012'
                        ':function:image-processor'
                    ),
                    'Events': ['s3:ObjectCreated:*'],
                    'Filter': {
                        'Key': {
                            'FilterRules': [
                                {'Name': 'prefix', 'Value': 'uploads/'},
                                {'Name': 'suffix', 'Value': '.jpg'},
                            ]
                        }
                    }
                }
            ]
        }
    )
    print("S3 → Lambda トリガーを設定しました")
