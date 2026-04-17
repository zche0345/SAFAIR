import {
  DynamoDBClient,
  GetItemCommand,
  PutItemCommand,
} from '@aws-sdk/client-dynamodb'
import { marshall, unmarshall } from '@aws-sdk/util-dynamodb'

const ddb = new DynamoDBClient({})
const TABLE_NAME = process.env.PREFERENCES_TABLE || 'user_profile'

const json = (statusCode, body) => ({
  statusCode,
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'GET,PATCH,OPTIONS',
  },
  body: JSON.stringify(body),
})

const getUserId = (event) =>
  event?.headers?.['x-anonymous-user-id'] ||
  event?.headers?.['X-Anonymous-User-Id'] ||
  null

export const handler = async (event) => {
  try {
    const method = event?.requestContext?.http?.method

    if (method === 'OPTIONS') {
      return json(200, {})
    }

    const userId = getUserId(event)
    if (!userId) {
      return json(400, { ok: false, message: 'Missing X-Anonymous-User-Id' })
    }

    if (method === 'GET') {
      const res = await ddb.send(
        new GetItemCommand({
          TableName: TABLE_NAME,
          Key: marshall({ userId }),
        })
      )

      const item = res.Item ? unmarshall(res.Item) : null

      return json(200, {
        ok: true,
        userId,
        preferences: item || {
          userId,
          locationEnabled: true,
          selectedSuburb: 'Melbourne',
          pushEnabled: false,
          pushSubscription: null,
          updatedAt: null,
        },
      })
    }

    // if (method === 'PATCH') {
    //   const body = event?.body ? JSON.parse(event.body) : {}
    //   const now = new Date().toISOString()

    //   const newItem = {
    //     userId,
    //     locationEnabled:
    //       typeof body.locationEnabled === 'boolean'
    //         ? body.locationEnabled
    //         : true,
    //     selectedSuburb:
    //       typeof body.selectedSuburb === 'string' && body.selectedSuburb.trim()
    //         ? body.selectedSuburb.trim()
    //         : 'Melbourne',
    //     pushEnabled:
    //       typeof body.pushEnabled === 'boolean'
    //         ? body.pushEnabled
    //         : false,
    //     pushSubscription:
    //       body.pushSubscription && typeof body.pushSubscription === 'object'
    //         ? body.pushSubscription
    //         : null,
    //     updatedAt: now,
    //   }

    //   await ddb.send(
    //     new PutItemCommand({
    //       TableName: TABLE_NAME,
    //       Item: marshall(newItem, { removeUndefinedValues: true }),
    //     })
    //   )

    //   return json(200, {
    //     ok: true,
    //     userId,
    //     preferences: newItem,
    //   })
    // }

    if (method === 'PATCH') {
      const body = event?.body ? JSON.parse(event.body) : {}
      const now = new Date().toISOString()
    
      const existingRes = await ddb.send(
        new GetItemCommand({
          TableName: TABLE_NAME,
          Key: marshall({ userId }),
        })
      )
    
      const existingItem = existingRes.Item ? unmarshall(existingRes.Item) : null
    
      const newItem = {
        userId,
        locationEnabled:
          typeof body.locationEnabled === 'boolean'
            ? body.locationEnabled
            : existingItem?.locationEnabled ?? true,
        selectedSuburb:
          typeof body.selectedSuburb === 'string' && body.selectedSuburb.trim()
            ? body.selectedSuburb.trim()
            : existingItem?.selectedSuburb ?? 'Melbourne',
        pushEnabled:
          typeof body.pushEnabled === 'boolean'
            ? body.pushEnabled
            : existingItem?.pushEnabled ?? false,
        pushSubscription:
          body.pushSubscription !== undefined
            ? body.pushSubscription
            : existingItem?.pushSubscription ?? null,
        updatedAt: now,
      }
    
      await ddb.send(
        new PutItemCommand({
          TableName: TABLE_NAME,
          Item: marshall(newItem, { removeUndefinedValues: true }),
        })
      )
    
      return json(200, { ok: true, userId, preferences: newItem })
    }

    return json(405, { ok: false, message: 'Method Not Allowed' })
  } catch (err) {
    console.error('user-preferences-api failed', err)
    return json(500, { ok: false, message: 'Internal server error' })
  }
}