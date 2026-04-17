import { DynamoDBClient, QueryCommand } from '@aws-sdk/client-dynamodb'
import { unmarshall } from '@aws-sdk/util-dynamodb'

const ddb = new DynamoDBClient({})
const TABLE_NAME = process.env.TABLE_NAME || 'air_snapshot'
const DEFAULT_LOCATION = process.env.DEFAULT_LOCATION || 'melbourne'

const json = (statusCode, body) => ({
  statusCode,
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  },
  body: JSON.stringify(body),
})

export const handler = async (event) => {
  try {
    const location =
      event?.queryStringParameters?.location?.trim().toLowerCase() ||
      DEFAULT_LOCATION

    const result = await ddb.send(
      new QueryCommand({
        TableName: TABLE_NAME,
        KeyConditionExpression: '#loc = :loc',
        ExpressionAttributeNames: { '#loc': 'location' },
        ExpressionAttributeValues: {
          ':loc': { S: location },
        },
        ScanIndexForward: false,
        Limit: 1,
      })
    )

    if (!result.Items || result.Items.length === 0) {
      return json(404, {
        ok: false,
        message: `No snapshot found for location: ${location}`,
      })
    }

    const item = unmarshall(result.Items[0])

    // Dynamic delay calculation at read time (required for AC)
    const nowMs = Date.now()
    const sourceMs = item.sourceTime ? new Date(item.sourceTime).getTime() : null
    const updatedMs = item.timestamp
      ? new Date(item.timestamp).getTime()
      : item.createdAt
        ? new Date(item.createdAt).getTime()
        : null

    const sourceAgeMinutes =
      sourceMs && Number.isFinite(sourceMs)
        ? Math.max(0, Math.round((nowMs - sourceMs) / 60000))
        : null

    const snapshotAgeMinutes =
      updatedMs && Number.isFinite(updatedMs)
        ? Math.max(0, Math.round((nowMs - updatedMs) / 60000))
        : null

    const isDelayed =
      (sourceAgeMinutes != null && sourceAgeMinutes > 90) ||
      (snapshotAgeMinutes != null && snapshotAgeMinutes > 90)

    return json(200, {
      ok: true,
      location: item.location,
      liveUpdateText: item.sourceTime
        ? `Live Update · ${new Date(item.sourceTime).toLocaleTimeString('en-AU', {
            hour: 'numeric',
            minute: '2-digit',
          })}`
        : null,
      lastUpdatedAt: item.timestamp || item.createdAt || null,
      statusTitle: item.statusTitle || null,
      statusSummary: item.statusSummary || null,
      aqi: item.aqi ?? null,
      aqiLabel: item.aqiLabel || null,
      isDelayed,
      sourceAgeMinutes,
      weather: item.weather || null,
      recommendations: item.recommendations || [],
    })
  } catch (err) {
    console.error('get-home-status failed', err)
    return json(500, {
      ok: false,
      message: 'Internal server error',
    })
  }
}
