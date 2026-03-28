// ソース記事: AWS CDK #4 — S3・Lambda・API GatewayでサーバーレスAPIを構築してみる
// Lambda ハンドラー: PUT /items/{id}（アイテム更新）

import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, UpdateCommand } from '@aws-sdk/lib-dynamodb';

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
    const body = JSON.parse(event.body || '{}');
    const keys = Object.keys(body);
    const expression = keys.map((k, i) => `#k${i} = :v${i}`).join(', ');
    const names: Record<string, string> = {};
    const values: Record<string, any> = {};
    keys.forEach((k, i) => {
      names[`#k${i}`] = k;
      values[`:v${i}`] = body[k];
    });

    const result = await docClient.send(
      new UpdateCommand({
        TableName: TABLE_NAME,
        Key: { id },
        UpdateExpression: `SET ${expression}, #updatedAt = :updatedAt`,
        ExpressionAttributeNames: { ...names, '#updatedAt': 'updatedAt' },
        ExpressionAttributeValues: { ...values, ':updatedAt': new Date().toISOString() },
        ReturnValues: 'ALL_NEW',
      })
    );

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result.Attributes),
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ message: 'Internal Server Error' }),
    };
  }
};
