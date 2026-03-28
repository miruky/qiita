import json
import boto3
import urllib.request

codepipeline = boto3.client('codepipeline')

def lambda_handler(event, context):
    job_id = event['CodePipeline.job']['id']
    
    try:
        # パイプラインの情報を取得
        user_params = json.loads(
            event['CodePipeline.job']['data']['actionConfiguration']['configuration'].get('UserParameters', '{}')
        )
        
        # Slack通知の送信
        slack_message = {
            "text": f"デプロイが完了しました！\n"
                    f"パイプライン: {user_params.get('pipeline', 'unknown')}\n"
                    f"ステージ: {user_params.get('stage', 'unknown')}"
        }
        
        webhook_url = user_params.get('webhook_url', '')
        if webhook_url:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(slack_message).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
        
        # 成功をCodePipelineに返す
        codepipeline.put_job_success_result(jobId=job_id)
        
    except Exception as e:
        # 失敗をCodePipelineに返す
        codepipeline.put_job_failure_result(
            jobId=job_id,
            failureDetails={
                'type': 'JobFailed',
                'message': str(e)
            }
        )
