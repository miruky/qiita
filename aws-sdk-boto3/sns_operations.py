"""
AWS SDK (Boto3) シリーズ #5
SNS トピック作成・サブスクリプション・メッセージ発行
"""

import json

import boto3


def create_topic():
    """SNS トピックを作成する"""
    sns = boto3.client('sns', region_name='ap-northeast-1')

    response = sns.create_topic(Name='my-notifications')
    topic_arn = response['TopicArn']
    print(f"トピック作成: {topic_arn}")
    return topic_arn


def add_subscriptions(topic_arn: str):
    """サブスクリプションを追加する"""
    sns = boto3.client('sns', region_name='ap-northeast-1')

    # Email サブスクリプション
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint='user@example.com'
    )

    # SQS サブスクリプション
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sqs',
        Endpoint='arn:aws:sqs:ap-northeast-1:123456789012:my-task-queue'
    )

    # Lambda サブスクリプション
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='lambda',
        Endpoint='arn:aws:lambda:ap-northeast-1:123456789012:function:my-handler'
    )

    # HTTPS サブスクリプション
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='https',
        Endpoint='https://example.com/webhook'
    )


def publish_simple(topic_arn: str):
    """シンプルなメッセージを発行する"""
    sns = boto3.client('sns', region_name='ap-northeast-1')

    response = sns.publish(
        TopicArn=topic_arn,
        Subject='デプロイ完了通知',
        Message='本番環境へのデプロイが完了しました。'
    )
    print(f"MessageId: {response['MessageId']}")


def publish_per_protocol(topic_arn: str):
    """プロトコル別にメッセージを送信する"""
    sns = boto3.client('sns', region_name='ap-northeast-1')

    message = {
        'default': 'デプロイが完了しました',
        'email': 'デプロイが完了しました。\n\n詳細はダッシュボードをご確認ください。',
        'sqs': json.dumps({'event': 'deploy_complete', 'env': 'production'}),
        'lambda': json.dumps({'action': 'post_deploy', 'version': '2.1.0'}),
    }

    sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps(message),
        MessageStructure='json'
    )


def subscribe_with_filter(topic_arn: str):
    """メッセージフィルタリング付きサブスクリプション"""
    sns = boto3.client('sns', region_name='ap-northeast-1')

    # フィルタポリシー付きサブスクリプション
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sqs',
        Endpoint='arn:aws:sqs:ap-northeast-1:123456789012:error-queue',
        Attributes={
            'FilterPolicy': json.dumps({
                'severity': ['ERROR', 'CRITICAL']
            })
        }
    )

    # フィルタに合致するメッセージを発行
    sns.publish(
        TopicArn=topic_arn,
        Message='データベース接続エラーが発生しました',
        MessageAttributes={
            'severity': {
                'DataType': 'String',
                'StringValue': 'ERROR'
            }
        }
    )
