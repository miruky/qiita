// ソース記事: AWS CDK #4 — S3・Lambda・API GatewayでサーバーレスAPIを構築してみる
// Lambda ハンドラー: DELETE /items/{id}（アイテム削除）

import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, DeleteCommand } from '@aws-sdk/lib-dynamodb';

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
    await docClient.send(
      new DeleteCommand({ TableName: TABLE_NAME, Key: { id } })
    );

    return {
      statusCode: 204,
      body: '',
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: 'Internal Server Error' }),
    };
  }
};
