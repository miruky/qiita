"""
Serverless REST API - Item CRUD
S3 をデータストアとして使用する Lambda ハンドラー
"""

import json
import uuid
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]
PREFIX = "items/"


def handler(event, context):
    """API Gateway HTTP API のイベントハンドラー"""
    http_method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "")
    path_params = event.get("pathParameters") or {}

    try:
        if path == "/items" and http_method == "GET":
            return list_items()
        elif path == "/items" and http_method == "POST":
            body = json.loads(event.get("body", "{}"))
            return create_item(body)
        elif "/items/" in path and http_method == "GET":
            return get_item(path_params["id"])
        elif "/items/" in path and http_method == "PUT":
            body = json.loads(event.get("body", "{}"))
            return update_item(path_params["id"], body)
        elif "/items/" in path and http_method == "DELETE":
            return delete_item(path_params["id"])
        else:
            return response(404, {"error": "Not Found"})
    except json.JSONDecodeError:
        return response(400, {"error": "Invalid JSON"})
    except Exception as e:
        print(f"Error: {e}")
        return response(500, {"error": "Internal Server Error"})


def list_items():
    """アイテム一覧を取得"""
    result = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
    items = []

    for obj in result.get("Contents", []):
        data = s3_client.get_object(Bucket=BUCKET_NAME, Key=obj["Key"])
        item = json.loads(data["Body"].read().decode("utf-8"))
        items.append(item)

    return response(200, {"items": items, "count": len(items)})


def create_item(body):
    """アイテムを作成"""
    item_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    item = {
        "id": item_id,
        "name": body.get("name", ""),
        "description": body.get("description", ""),
        "created_at": now,
        "updated_at": now,
    }

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"{PREFIX}{item_id}.json",
        Body=json.dumps(item, ensure_ascii=False),
        ContentType="application/json",
    )

    return response(201, item)


def get_item(item_id):
    """アイテムを取得"""
    try:
        data = s3_client.get_object(
            Bucket=BUCKET_NAME, Key=f"{PREFIX}{item_id}.json"
        )
        item = json.loads(data["Body"].read().decode("utf-8"))
        return response(200, item)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return response(404, {"error": "Item not found"})
        raise


def update_item(item_id, body):
    """アイテムを更新"""
    try:
        data = s3_client.get_object(
            Bucket=BUCKET_NAME, Key=f"{PREFIX}{item_id}.json"
        )
        item = json.loads(data["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return response(404, {"error": "Item not found"})
        raise

    item["name"] = body.get("name", item["name"])
    item["description"] = body.get("description", item["description"])
    item["updated_at"] = datetime.now(timezone.utc).isoformat()

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=f"{PREFIX}{item_id}.json",
        Body=json.dumps(item, ensure_ascii=False),
        ContentType="application/json",
    )

    return response(200, item)


def delete_item(item_id):
    """アイテムを削除"""
    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=f"{PREFIX}{item_id}.json")
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return response(404, {"error": "Item not found"})
        raise

    s3_client.delete_object(
        Bucket=BUCKET_NAME, Key=f"{PREFIX}{item_id}.json"
    )
    return response(204, None)


def response(status_code, body):
    """HTTP レスポンスを生成"""
    result = {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }
    if body is not None:
        result["body"] = json.dumps(body, ensure_ascii=False)
    return result
