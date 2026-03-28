"""
AWS SDK (Boto3) シリーズ #1
はじめての Boto3 コード — 基本的な API 呼び出し
"""

import boto3


def list_s3_buckets():
    """S3 バケット一覧を取得する"""
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    print("=== S3 バケット一覧 ===")
    for bucket in response['Buckets']:
        print(f"  {bucket['Name']}  (作成日: {bucket['CreationDate']})")


def list_ec2_instances():
    """EC2 インスタンス一覧を取得する"""
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    response = ec2.describe_instances()

    print("=== EC2 インスタンス一覧 ===")
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            name = ''
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']

            print(f"  {instance['InstanceId']}  "
                  f"State: {instance['State']['Name']}  "
                  f"Type: {instance['InstanceType']}  "
                  f"Name: {name}")


def get_caller_identity():
    """STS で自分のアカウント情報を確認する"""
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()

    print(f"アカウントID: {identity['Account']}")
    print(f"ユーザーARN:  {identity['Arn']}")
    print(f"ユーザーID:   {identity['UserId']}")


def list_iam_users():
    """IAM ユーザー一覧を取得する"""
    iam = boto3.client('iam')
    response = iam.list_users()

    print("=== IAM ユーザー一覧 ===")
    for user in response['Users']:
        print(f"  {user['UserName']}  (作成日: {user['CreateDate']})")


def list_regions():
    """利用可能なリージョン一覧を取得する"""
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()

    print("=== 利用可能なリージョン ===")
    for region in sorted(response['Regions'], key=lambda r: r['RegionName']):
        print(f"  {region['RegionName']}")


if __name__ == '__main__':
    get_caller_identity()
    list_s3_buckets()
    list_ec2_instances()
    list_iam_users()
    list_regions()
