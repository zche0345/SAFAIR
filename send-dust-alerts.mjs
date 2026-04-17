import webpush from 'web-push'
import {
  DynamoDBClient,
  GetItemCommand,
  ScanCommand,
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
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
  },
  body: JSON.stringify(body),
})

const hasValidSubscription = (subscription) => {
  return Boolean(
    subscription &&
      subscription.endpoint &&
      subscription.keys &&
      subscription.keys.p256dh &&
      subscription.keys.auth
  )
}

export const handler = async (event) => {
  try {
    const method = event?.requestContext?.http?.method

    if (method === 'OPTIONS') {
      return json(200, {})
    }

    if (method !== 'POST') {
      return json(405, { ok: false, message: 'Method Not Allowed' })
    }

    const vapidSubject = process.env.VAPID_SUBJECT
    const vapidPublicKey = process.env.VAPID_PUBLIC_KEY
    const vapidPrivateKey = process.env.VAPID_PRIVATE_KEY

    if (!vapidSubject || !vapidPublicKey || !vapidPrivateKey) {
      return json(500, {
        ok: false,
        message: 'Missing VAPID environment variables',
      })
    }

    webpush.setVapidDetails(vapidSubject, vapidPublicKey, vapidPrivateKey)

    const body = event?.body ? JSON.parse(event.body) : {}
    const testUserId = body.userId || null
    const suburbWithRiskSpike = body.suburb || 'Melbourne'

    let targets = []

    // TEST MODE: fetch exact user directly
    if (testUserId) {
      const result = await ddb.send(
        new GetItemCommand({
          TableName: TABLE_NAME,
          Key: marshall({ userId: testUserId }),
        })
      )

      const user = result.Item ? unmarshall(result.Item) : null

      if (!user) {
        return json(404, {
          ok: false,
          message: `User not found: ${testUserId}`,
        })
      }

      if (!user.pushEnabled) {
        return json(400, {
          ok: false,
          message: 'Push is disabled for this user',
          user,
        })
      }

      if (!hasValidSubscription(user.pushSubscription)) {
        return json(400, {
          ok: false,
          message: 'Push subscription is missing or incomplete',
          pushSubscription: user.pushSubscription || null,
        })
      }

      targets = [user]
    } else {
      // NORMAL MODE
      const result = await ddb.send(
        new ScanCommand({
          TableName: TABLE_NAME,
        })
      )

      const users = (result.Items || []).map(unmarshall)

      targets = users.filter(
        (u) =>
          u.pushEnabled === true &&
          u.selectedSuburb === suburbWithRiskSpike &&
          hasValidSubscription(u.pushSubscription)
      )

      if (!targets.length) {
        return json(404, {
          ok: false,
          message: 'No subscribed users found for this suburb',
        })
      }
    }

    const payload = JSON.stringify({
      title: testUserId ? 'SAFAIR Test Alert' : 'Dust risk rising near you',
      body: testUserId
        ? 'Push notifications are working on this device.'
        : `Construction dust levels have increased in ${suburbWithRiskSpike}. Keep windows closed and reduce outdoor activity.`,
      url: '/construction-dust',
    })

    let sent = 0
    const failed = []

    for (const user of targets) {
      try {
        await webpush.sendNotification(user.pushSubscription, payload)
        sent += 1
      } catch (err) {
        console.error('Push failed for user', user.userId, err)
        failed.push({
          userId: user.userId,
          statusCode: err?.statusCode || null,
          message: err?.message || 'Unknown error',
        })
      }
    }

    return json(200, {
      ok: true,
      sent,
      failed,
      testMode: Boolean(testUserId),
    })
  } catch (err) {
    console.error('send-dust-alerts failed', err)
    return json(500, {
      ok: false,
      message: 'Internal server error',
      error: err?.message || 'Unknown error',
    })
  }
}