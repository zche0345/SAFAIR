import {
  DynamoDBClient,
  PutItemCommand,
  DeleteItemCommand,
  QueryCommand,
  BatchWriteItemCommand,
} from '@aws-sdk/client-dynamodb';
import { marshall, unmarshall } from '@aws-sdk/util-dynamodb';

const ddb = new DynamoDBClient({});
const TABLE_NAME = process.env.PUSH_TABLE || 'push_subscriptions';

const json = (statusCode, body) => ({
  statusCode,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});

const getUserId = (event) =>
  event?.headers?.['x-anonymous-user-id'] ||
  event?.headers?.['X-Anonymous-User-Id'] ||
  null;

const getPath = (event) => event?.rawPath || '';

export const handler = async (event) => {
  try {
    const method = event?.requestContext?.http?.method;
    const path = getPath(event);
    const userId = getUserId(event);

    if (!userId) return json(400, { ok: false, message: 'Missing X-Anonymous-User-Id' });
    if (method !== 'POST') return json(405, { ok: false, message: 'Method Not Allowed' });

    const body = event?.body ? JSON.parse(event.body) : {};
    const now = new Date().toISOString();

    if (path.endsWith('/subscribe')) {
      const subscription = body.subscription || {};
      const endpoint = subscription.endpoint;

      if (!endpoint) {
        return json(400, { ok: false, message: 'subscription.endpoint is required' });
      }

      const item = {
        userId,
        endpoint, // sort key
        keys: subscription.keys || {},
        platform: body.platform || 'web',
        enabled: body.enabled !== false,
        createdAt: now,
        updatedAt: now,
      };

      await ddb.send(
        new PutItemCommand({
          TableName: TABLE_NAME,
          Item: marshall(item, { removeUndefinedValues: true }),
        })
      );

      return json(200, { ok: true, message: 'Subscribed', endpoint });
    }

    if (path.endsWith('/unsubscribe')) {
      const endpoint = body.endpoint;

      if (endpoint) {
        await ddb.send(
          new DeleteItemCommand({
            TableName: TABLE_NAME,
            Key: marshall({ userId, endpoint }),
          })
        );
        return json(200, { ok: true, message: 'Unsubscribed', endpoint });
      }

      // endpoint 
      const q = await ddb.send(
        new QueryCommand({
          TableName: TABLE_NAME,
          KeyConditionExpression: '#u = :u',
          ExpressionAttributeNames: { '#u': 'userId' },
          ExpressionAttributeValues: { ':u': { S: userId } },
        })
      );

      const items = (q.Items || []).map(unmarshall);
      if (!items.length) return json(200, { ok: true, message: 'No subscriptions found' });

      // batch delete (25/sets)
      for (let i = 0; i < items.length; i += 25) {
        const chunk = items.slice(i, i + 25);
        await ddb.send(
          new BatchWriteItemCommand({
            RequestItems: {
              [TABLE_NAME]: chunk.map((x) => ({
                DeleteRequest: { Key: marshall({ userId: x.userId, endpoint: x.endpoint }) },
              })),
            },
          })
        );
      }

      return json(200, { ok: true, message: 'All subscriptions removed', count: items.length });
    }

    return json(404, { ok: false, message: 'Route not found' });
  } catch (err) {
    console.error('push-subscription-api failed', err);
    return json(500, { ok: false, message: 'Internal server error' });
  }
};
