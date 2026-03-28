"""
AWS SDK (Boto3) シリーズ #5
SQS キュー作成・メッセージ送受信・DLQ 設定
"""

import json

import boto3


def create_standard_queue():
    """標準キューを作成する"""
    sqs = boto3.client('sqs', region_name='ap-northeast-1')

    response = sqs.create_queue(
        QueueName='my-task-queue',
        Attributes={
            'VisibilityTimeout': '60',            # 可視性タイムアウト（秒）
            'MessageRetentionPeriod': '86400',     # メッセージ保持期間（1 日）
            'ReceiveMessageWaitTimeSeconds': '10',  # ロングポーリング
        }
    )
    queue_url = response['QueueUrl']
    print(f"キュー作成: {queue_url}")
    return queue_url


def create_fifo_queue():
    """FIFO キューを作成する"""
    sqs = boto3.client('sqs', region_name='ap-northeast-1')

    response = sqs.create_queue(
        QueueName='my-order-queue.fifo',  # .fifo が必須
        Attributes={
            'FifoQueue': 'true',
            'ContentBasedDeduplication': 'true',  # メッセージ本文でデデュプ
        }
    )
    return response['QueueUrl']


def send_message(queue_url: str):
    """単一メッセージを送信する"""
    sqs = boto3.client('sqs')

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({
            'task': 'process_image',
            'image_id': 'img-001',
            'format': 'png'
        }),
        MessageAttributes={
            'Priority': {
                'DataType': 'String',
                'StringValue': 'high'
            }
        }
    )
    print(f"MessageId: {response['MessageId']}")


def send_message_batch(queue_url: str):
    """メッセージを一括送信する"""
    sqs = boto3.client('sqs')

    entries = []
    for i in range(10):
        entries.append({
            'Id': str(i),
            'MessageBody': json.dumps({'task_id': i, 'action': 'process'}),
        })

    response = sqs.send_message_batch(
        QueueUrl=queue_url,
        Entries=entries
    )

    print(f"成功: {len(response.get('Successful', []))} 件")
    print(f"失敗: {len(response.get('Failed', []))} 件")


def receive_and_delete(queue_url: str):
    """メッセージを受信して処理後に削除する"""
    sqs = boto3.client('sqs')

    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=5,       # 最大 10
        WaitTimeSeconds=10,          # ロングポーリング
        MessageAttributeNames=['All'],
        AttributeNames=['All']
    )

    messages = response.get('Messages', [])
    print(f"受信: {len(messages)} 件")

    for msg in messages:
        body = json.loads(msg['Body'])
        print(f"  MessageId: {msg['MessageId']}")
        print(f"  Body: {body}")

        # 処理が完了したら削除
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=msg['ReceiptHandle']
        )
        print("  → 削除完了")


def setup_dead_letter_queue(queue_url: str):
    """デッドレターキュー（DLQ）を設定する"""
    sqs = boto3.client('sqs')

    # DLQ を作成
    dlq_response = sqs.create_queue(QueueName='my-task-dlq')
    dlq_url = dlq_response['QueueUrl']

    # DLQ の ARN を取得
    dlq_attrs = sqs.get_queue_attributes(
        QueueUrl=dlq_url,
        AttributeNames=['QueueArn']
    )
    dlq_arn = dlq_attrs['Attributes']['QueueArn']

    # メインキューに DLQ を設定
    sqs.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={
            'RedrivePolicy': json.dumps({
                'deadLetterTargetArn': dlq_arn,
                'maxReceiveCount': '3'  # 3 回失敗で DLQ へ
            })
        }
    )
    print("DLQ を設定しました")
