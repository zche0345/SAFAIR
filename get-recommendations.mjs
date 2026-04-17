import { DynamoDBClient, QueryCommand } from '@aws-sdk/client-dynamodb'
import { unmarshall } from '@aws-sdk/util-dynamodb'

const ddb = new DynamoDBClient({})
const TABLE_NAME = process.env.TABLE_NAME || 'air_snapshot'
const DEFAULT_LOCATION = process.env.DEFAULT_LOCATION || 'melbourne'

const AIR_API = 'https://air-quality-api.open-meteo.com/v1/air-quality'
const DEFAULT_LATITUDE = Number(process.env.DEFAULT_LATITUDE || -37.8136)
const DEFAULT_LONGITUDE = Number(process.env.DEFAULT_LONGITUDE || 144.9631)
const DEFAULT_TIMEZONE = process.env.DEFAULT_TIMEZONE || 'Australia/Sydney'

const LOCATION_CONFIG = {
  melbourne: {
    latitude: -37.8136,
    longitude: 144.9631,
    timezone: 'Australia/Sydney',
  },
}

const WINDOWS = [
  { label: '06:00-10:00', startHour: 6, endHour: 10 },
  { label: '10:00-14:00', startHour: 10, endHour: 14 },
  { label: '14:00-18:00', startHour: 14, endHour: 18 },
  { label: '18:00-22:00', startHour: 18, endHour: 22 },
]

const json = (statusCode, body) => ({
  statusCode,
  headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  },
  body: JSON.stringify(body),
})

function parseHourLocal(timeIsoLike) {
  return Number(timeIsoLike.slice(11, 13))
}

function parseDateLocal(timeIsoLike) {
  return timeIsoLike.slice(0, 10)
}

function toNumber(v) {
  return typeof v === 'number' && Number.isFinite(v) ? v : null
}

function avg(values) {
  const nums = values.filter((v) => typeof v === 'number' && Number.isFinite(v))
  if (!nums.length) return null
  return nums.reduce((a, b) => a + b, 0) / nums.length
}

function normalizeAqi(aqi) {
  if (aqi == null) return 60
  return Math.min(Math.max(aqi, 0), 200) / 200
}

function normalizePm25(pm25) {
  if (pm25 == null) return 0.4
  return Math.min(Math.max(pm25, 0), 75) / 75
}

function normalizeOzone(ozone) {
  if (ozone == null) return 0.4
  return Math.min(Math.max(ozone, 0), 240) / 240
}

function normalizeNo2(no2) {
  if (no2 == null) return 0.3
  return Math.min(Math.max(no2, 0), 200) / 200
}

function scoreHour({ aqi, pm25, ozone, no2 }) {
  const score =
    normalizeAqi(aqi) * 0.5 +
    normalizePm25(pm25) * 0.25 +
    normalizeOzone(ozone) * 0.15 +
    normalizeNo2(no2) * 0.1

  return Number(score.toFixed(4))
}

function levelFromScore(score) {
  if (score <= 0.35) return 'safe'
  if (score <= 0.6) return 'caution'
  return 'avoid'
}

function severityFromSnapshot(item) {
  const label = (item?.aqiLabel || '').toLowerCase()
  const title = (item?.statusTitle || '').toLowerCase()

  if (label === 'good' || title.includes('low asthma risk')) return 'low'
  if (label === 'moderate' || title.includes('moderate asthma risk')) return 'moderate'
  if (label.includes('sensitive') || title.includes('high asthma risk')) return 'high'
  if (label === 'unhealthy' || title.includes('very high asthma risk')) return 'very_high'
  return 'moderate'
}

async function getLatestSnapshot(location) {
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
    return null
  }

  return unmarshall(result.Items[0])
}

async function getOutdoorPlan(location) {
  const cfg = LOCATION_CONFIG[location] || {
    latitude: DEFAULT_LATITUDE,
    longitude: DEFAULT_LONGITUDE,
    timezone: DEFAULT_TIMEZONE,
  }

  const url =
    `${AIR_API}?latitude=${cfg.latitude}&longitude=${cfg.longitude}` +
    `&hourly=us_aqi,pm2_5,pm10,ozone,nitrogen_dioxide` +
    `&timezone=${encodeURIComponent(cfg.timezone)}`

  const res = await fetch(url)
  if (!res.ok) throw new Error(`Air API failed: ${res.status}`)

  const data = await res.json()
  const times = data?.hourly?.time || []
  const aqiArr = data?.hourly?.us_aqi || []
  const pm25Arr = data?.hourly?.pm2_5 || []
  const ozoneArr = data?.hourly?.ozone || []
  const no2Arr = data?.hourly?.nitrogen_dioxide || []

  if (!times.length) {
    return {
      safest: null,
      riskiest: null,
    }
  }

  const today = new Intl.DateTimeFormat('en-CA', {
    timeZone: cfg.timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date())

  const todayHours = []
  for (let i = 0; i < times.length; i++) {
    if (parseDateLocal(times[i]) !== today) continue

    todayHours.push({
      hour: parseHourLocal(times[i]),
      aqi: toNumber(aqiArr[i]),
      pm25: toNumber(pm25Arr[i]),
      ozone: toNumber(ozoneArr[i]),
      no2: toNumber(no2Arr[i]),
    })
  }

  if (!todayHours.length) {
    return {
      safest: null,
      riskiest: null,
    }
  }

  const windowResults = WINDOWS.map((w) => {
    const rows = todayHours.filter((r) => r.hour >= w.startHour && r.hour < w.endHour)

    if (!rows.length) {
      return {
        label: w.label,
        level: 'caution',
        score: 0.6,
      }
    }

    const score = avg(rows.map((r) => scoreHour(r))) ?? 0.6

    return {
      label: w.label,
      level: levelFromScore(score),
      score: Number(score.toFixed(4)),
    }
  })

  const safest = [...windowResults].sort((a, b) => a.score - b.score)[0]
  const riskiest = [...windowResults].sort((a, b) => b.score - a.score)[0]

  return { safest, riskiest }
}

function buildPayload({ item, severity, outdoorPlan }) {
  const bestWindow = outdoorPlan?.safest?.label || '06:00-10:00'
  const riskyWindow = outdoorPlan?.riskiest?.label || '14:00-18:00'

  const content = {
    low: {
      supportTitle: "You've got this 💚",
      supportText:
        "Today's conditions look fairly manageable. These are light, practical suggestions to help your child stay comfortable.",
      home: [
        {
          id: 'home-1',
          title: 'Keep their inhaler somewhere easy to find',
          description:
            'Even on lower-risk days, it helps to know exactly where it is.',
        },
        {
          id: 'home-2',
          title: 'Stick to your normal routine',
          description:
            'Most indoor activities should feel comfortable today.',
        },
        {
          id: 'home-3',
          title: 'Let fresh air in if your child feels okay',
          description:
            'Conditions are generally reasonable today, so normal ventilation is usually fine.',
        },
      ],
      school: [
        {
          id: 'school-1',
          title: 'Pack their inhaler in their school bag',
          description:
            'It is always better to be prepared, even on a good day.',
        },
        {
          id: 'school-2',
          title: 'Normal school activity is usually okay',
          description:
            'Children can generally follow their regular school routine if they feel well.',
        },
        {
          id: 'school-3',
          title: 'Encourage water breaks',
          description:
            'Simple habits like hydration still help them feel their best.',
        },
      ],
      outdoor: [
        {
          id: 'outdoor-1',
          title: `Best time for outdoor play: ${bestWindow}`,
          description:
            'This looks like the gentlest window if your child wants to be active outside.',
        },
        {
          id: 'outdoor-2',
          title: 'Keep an eye on symptoms during active play',
          description:
            'If they start coughing or wheezing, reduce intensity and take a break.',
        },
        {
          id: 'outdoor-3',
          title: 'Use normal sun and hydration precautions',
          description:
            'Comfort still matters even on a more manageable day.',
        },
      ],
    },
    moderate: {
      supportTitle: "You've got this 💚",
      supportText:
        "Today's conditions need a little more care. Small steps can make a real difference in keeping your child comfortable.",
      home: [
        {
          id: 'home-1',
          title: 'Keep windows closed in the afternoon',
          description:
            'Pollen and pollution can feel more irritating later in the day.',
        },
        {
          id: 'home-2',
          title: 'Use air conditioning with a clean filter',
          description:
            'A good filter helps reduce irritating particles indoors.',
        },
        {
          id: 'home-3',
          title: 'Have their reliever inhaler easily accessible',
          description:
            'Quick access helps if symptoms begin unexpectedly.',
        },
      ],
      school: [
        {
          id: 'school-1',
          title: 'Pack their inhaler in their school bag',
          description:
            'Make sure teachers know where it is and can access it if needed.',
        },
        {
          id: 'school-2',
          title: 'Consider indoor activities for PE today',
          description:
            'Outdoor exercise may be more irritating than usual.',
        },
        {
          id: 'school-3',
          title: 'Remind them to stay hydrated',
          description:
            'Drinking water can help them feel more comfortable through the day.',
        },
      ],
      outdoor: [
        {
          id: 'outdoor-1',
          title: `Limit outdoor time during ${riskyWindow}`,
          description:
            'This is likely to be the most irritating part of the day for sensitive breathing.',
        },
        {
          id: 'outdoor-2',
          title: `Prefer outdoor play during ${bestWindow}`,
          description:
            'If they do go outside, this is the better time window.',
        },
        {
          id: 'outdoor-3',
          title: 'Watch for early warning signs',
          description:
            "Coughing, wheezing, or chest tightness means it's time to head inside.",
        },
      ],
    },
    high: {
      supportTitle: "You've got this 💚",
      supportText:
        "Today is a higher-risk day. It is a good idea to be more cautious and reduce exposure where possible.",
      home: [
        {
          id: 'home-1',
          title: 'Keep windows closed during peak hours',
          description:
            'This helps keep pollen and pollution out of the home.',
        },
        {
          id: 'home-2',
          title: 'Use filtered indoor air if possible',
          description:
            'Air conditioning or an air purifier can help create a calmer indoor space.',
        },
        {
          id: 'home-3',
          title: 'Keep asthma medication close by',
          description:
            'Be ready to respond quickly if symptoms begin.',
        },
      ],
      school: [
        {
          id: 'school-1',
          title: 'Tell school staff it is a higher-risk day',
          description:
            'Extra awareness helps them respond earlier if symptoms show up.',
        },
        {
          id: 'school-2',
          title: 'Avoid strenuous outdoor PE if possible',
          description:
            'Running and other high-intensity activity may trigger symptoms today.',
        },
        {
          id: 'school-3',
          title: 'Double-check inhaler access before leaving home',
          description:
            'Preparation matters more on days like this.',
        },
      ],
      outdoor: [
        {
          id: 'outdoor-1',
          title: `Avoid the riskiest window: ${riskyWindow}`,
          description:
            'This part of the day looks least suitable for sensitive lungs.',
        },
        {
          id: 'outdoor-2',
          title: `Use the safest window only if needed: ${bestWindow}`,
          description:
            'If outdoor time cannot be avoided, this is the gentler option.',
        },
        {
          id: 'outdoor-3',
          title: 'Move indoors at the first sign of symptoms',
          description:
            'Do not wait if coughing, wheezing, or chest tightness begins.',
        },
      ],
    },
    very_high: {
      supportTitle: "You've got this 💚",
      supportText:
        "Today is a very high-risk day. Indoor plans and close symptom monitoring are the safest approach.",
      home: [
        {
          id: 'home-1',
          title: 'Keep the home closed up during the day',
          description:
            'Try to reduce outside air entering if conditions feel poor.',
        },
        {
          id: 'home-2',
          title: 'Stay indoors as much as possible',
          description:
            'Indoor time is the safer option today.',
        },
        {
          id: 'home-3',
          title: "Follow your child's asthma action plan closely",
          description:
            'Use your normal medical guidance if symptoms appear or worsen.',
        },
      ],
      school: [
        {
          id: 'school-1',
          title: 'Let school staff know outdoor exposure should be limited',
          description:
            'Teachers should be extra cautious today.',
        },
        {
          id: 'school-2',
          title: 'Prefer indoor classes and break-time options',
          description:
            'Reducing outside exposure can help avoid symptom triggers.',
        },
        {
          id: 'school-3',
          title: 'Make sure the inhaler is packed and easy to access',
          description:
            'Today is not the day to be without it.',
        },
      ],
      outdoor: [
        {
          id: 'outdoor-1',
          title: 'Avoid outdoor activity where possible',
          description:
            'Indoor alternatives are the safest choice today.',
        },
        {
          id: 'outdoor-2',
          title: `If you must go out, use the least risky window: ${bestWindow}`,
          description:
            'Keep the outing short and low intensity.',
        },
        {
          id: 'outdoor-3',
          title: 'Head inside immediately if symptoms appear',
          description:
            'Take early signs seriously and follow the action plan.',
        },
      ],
    },
  }

  const selected = content[severity] || content.moderate

  return {
    ok: true,
    location: item.location || DEFAULT_LOCATION,
    lastUpdatedAt: item.timestamp || item.createdAt || null,
    severity,
    heroTitle: 'Your action plan for today',
    heroSubtitle: 'Simple steps to keep your child safe and comfortable',
    supportCard: {
      title: selected.supportTitle,
      text: selected.supportText,
    },
    sections: [
      {
        id: 'home',
        title: 'At Home',
        emoji: '🏡',
        icon: '⌂',
        subtitle: 'Create a safe, comfortable environment indoors',
        items: selected.home,
      },
      {
        id: 'school',
        title: 'At School',
        emoji: '🎒',
        icon: '⌘',
        subtitle: 'Help teachers keep your child safe while learning',
        items: selected.school,
      },
      {
        id: 'outdoor',
        title: 'Outdoor Activities',
        emoji: '🌳',
        icon: '△',
        subtitle: 'Stay safe when playing outside',
        items: selected.outdoor,
      },
    ],
    footerCard: {
      title: 'Every child is unique',
      text:
        "These are gentle guidelines based on today's environmental conditions in Melbourne. Always follow your child's personal asthma action plan, trust your parental instincts, and don't hesitate to reach out to your healthcare provider if you have concerns or if symptoms worsen.",
      closingLine: "You're doing a great job taking care of your child. 💛",
    },
  }
}

export const handler = async (event) => {
  try {
    const location =
      event?.queryStringParameters?.location?.trim().toLowerCase() ||
      DEFAULT_LOCATION

    const item = await getLatestSnapshot(location)

    if (!item) {
      return json(404, {
        ok: false,
        message: `No snapshot found for location: ${location}`,
      })
    }

    const severity = severityFromSnapshot(item)
    const outdoorPlan = await getOutdoorPlan(location)

    return json(200, buildPayload({ item, severity, outdoorPlan }))
  } catch (err) {
    console.error('get-recommendations failed', err)
    return json(500, {
      ok: false,
      message: 'Internal server error',
    })
  }
}