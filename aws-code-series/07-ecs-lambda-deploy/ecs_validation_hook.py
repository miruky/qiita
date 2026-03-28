import boto3
import json
import urllib.request

codedeploy = boto3.client('codedeploy')

def lambda_handler(event, context):
    deployment_id = event['DeploymentId']
    lifecycle_event_hook_execution_id = event['LifecycleEventHookExecutionId']
    
    try:
        # テストリスナーのURLにアクセスして検証
        test_url = "http://test-alb-url:8080/health"
        response = urllib.request.urlopen(test_url, timeout=10)
        
        if response.getcode() == 200:
            status = 'Succeeded'
            print("Health check passed!")
        else:
            status = 'Failed'
            print(f"Health check failed with status: {response.getcode()}")
    except Exception as e:
        status = 'Failed'
        print(f"Error: {str(e)}")
    
    # CodeDeployにステータスを返す
    codedeploy.put_lifecycle_event_hook_execution_status(
        deploymentId=deployment_id,
        lifecycleEventHookExecutionId=lifecycle_event_hook_execution_id,
        status=status
    )
    
    return {'statusCode': 200, 'body': json.dumps({'status': status})}
