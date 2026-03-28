// ソース記事: AWS CDK #4 — S3・Lambda・API GatewayでサーバーレスAPIを構築してみる
// Lambda ハンドラー: GET /items/{id}（アイテム取得）

import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand } from '@aws-sdk/lib-dynamodb';

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);
const TABLE_NAME = process.env.TABLE_NAME!;

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  const id = event.pathParameters?.id;
  if (!id) {
    return { statusCode: 400, body: JSON.stringify({ message: 'Missing id' }) };
  }

  try {
    const result = await docClient.send(
      new GetCommand({ TableName: TABLE_NAME, Key: { id } })
    );

    if (!result.Item) {
      return { statusCode: 404, body: JSON.stringify({ message: 'Not Found' }) };
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result.Item),
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: 'Internal Server Error' }),
    };
  }
};
