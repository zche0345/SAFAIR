// index.mjs
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

const toNum = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null)

const valueWithUnit = (value, unit) => {
  if (value == null) return '--'
  return `${value}${unit}`
}

const pm25Level = (v) => {
  if (v == null) return { label: 'Unknown', theme: 'amber' }
  if (v <= 12) return { label: 'Good', theme: 'mint' }
  if (v <= 35.4) return { label: 'Moderate', theme: 'amber' }
  return { label: 'High', theme: 'pink' }
}

const pm10Level = (v) => {
  if (v == null) return { label: 'Unknown', theme: 'amber' }
  if (v <= 54) return { label: 'Good', theme: 'mint' }
  if (v <= 154) return { label: 'Moderate', theme: 'amber' }
  return { label: 'High', theme: 'pink' }
}

const ozoneLevel = (v) => {
  if (v == null) return { label: 'Unknown', theme: 'amber' }
  if (v <= 100) return { label: 'Good', theme: 'mint' } // ug/m3
  if (v <= 160) return { label: 'Moderate', theme: 'amber' }
  return { label: 'High', theme: 'pink' }
}

const no2Level = (v) => {
  if (v == null) return { label: 'Unknown', theme: 'amber' }
  if (v <= 80) return { label: 'Good', theme: 'mint' } // ug/m3
  if (v <= 200) return { label: 'Moderate', theme: 'amber' }
  return { label: 'High', theme: 'pink' }
}

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
    const pollutants = item.pollutants || {}

    const pm25 = toNum(pollutants.pm25)
    const pm10 = toNum(pollutants.pm10)
    const ozone = toNum(pollutants.ozone)
    const no2 = toNum(pollutants.no2)

    const pm25Meta = pm25Level(pm25)
    const pm10Meta = pm10Level(pm10)
    const ozoneMeta = ozoneLevel(ozone)
    const no2Meta = no2Level(no2)

    const summaryTitle =
      item.aqiLabel === 'Good'
        ? 'Low Risk Today'
        : item.aqiLabel === 'Moderate'
          ? 'Moderate Risk Today'
          : 'Higher Risk Today'

    const summaryText =
      item.statusSummary ||
      "A few environmental factors are elevated today. Here's what you should know."

    const factors = [
      {
        title: 'PM2.5',
        icon: '☁',
        value: valueWithUnit(pm25, ' ug/m³'),
        description: `Fine particles are ${pm25Meta.label.toLowerCase()} today.`,
        note:
          pm25Meta.label === 'High'
            ? 'May trigger symptoms during outdoor activity.'
            : 'Usually manageable with basic precautions.',
        explanation:
          'PM2.5 can reach deep into the lungs and may worsen asthma symptoms in sensitive children.',
        theme: pm25Meta.theme,
      },
      {
        title: 'PM10',
        icon: '≋',
        value: valueWithUnit(pm10, ' ug/m³'),
        description: `Coarser particles are ${pm10Meta.label.toLowerCase()} today.`,
        note:
          pm10Meta.label === 'High'
            ? 'Limit prolonged outdoor exposure if symptoms appear.'
            : 'Keep normal activity with awareness.',
        explanation:
          'PM10 can irritate the airways and may increase cough or chest tightness.',
        theme: pm10Meta.theme,
      },
      {
        title: 'Ozone (O3)',
        icon: '◔',
        value: valueWithUnit(ozone, ' ug/m³'),
        description: `Ozone levels are ${ozoneMeta.label.toLowerCase()} right now.`,
        note:
          ozoneMeta.label === 'High'
            ? 'Afternoon exercise may be less comfortable.'
            : 'No major concern at current levels.',
        explanation:
          'Ozone can inflame sensitive airways and is often worse later in the day.',
        theme: ozoneMeta.theme,
      },
      {
        title: 'NO2',
        icon: '◍',
        value: valueWithUnit(no2, ' ug/m³'),
        description: `Traffic-related NO₂ is ${no2Meta.label.toLowerCase()} today.`,
        note:
          no2Meta.label === 'High'
            ? 'Avoid busy roads when possible.'
            : 'Prefer cleaner routes for outdoor activity.',
        explanation:
          'NO₂ can increase airway sensitivity, especially near high-traffic areas.',
        theme: no2Meta.theme,
      },
    ]

    return json(200, {
      ok: true,
      location,
      lastUpdatedAt: item.timestamp || item.createdAt || null,
      summaryTitle,
      summaryText,
      factors,
    })
  } catch (err) {
    console.error('get-insights failed', err)
    return json(500, {
      ok: false,
      message: 'Internal server error',
    })
  }
}
