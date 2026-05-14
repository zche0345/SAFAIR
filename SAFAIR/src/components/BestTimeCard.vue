<template>
  <section class="best-time-section reveal">
    <div class="best-time-inner">
      <div class="best-time-content">
        <div class="timing-label">
          <span class="timing-dot"></span>
          <span>Timing matters</span>
        </div>

        <div class="best-time-headline-row">
          <div class="best-time-copy">
            <h2>When is the best time<br />to go outside today?</h2>
            <p>
              Air quality shifts throughout the day -- sometimes quite sharply. We
              find the gentlest window so you don't have to guess.
            </p>
          </div>

          <aside class="best-window" aria-label="Best outdoor window today">
            <p>Best window today</p>
            <strong>{{ formatHour(bestTime.hour) }}</strong>
            <span>{{ bestTimeReason }}</span>
          </aside>
        </div>

        <div class="prototype-chart" role="img" aria-label="Hourly outdoor air quality comparison">
          <div
            v-for="(hour, index) in hourlyForecast"
            :key="`${hour.hour}-${index}`"
            class="prototype-bar-item"
            :class="[levelClass(hour.level), { active: isBestHour(hour) }]"
            :title="`${formatHour(hour.hour)}: ${riskLabel(hour.level)} (${hour.score}/100)`"
            :style="{ transitionDelay: `${index * 0.035}s` }"
          >
            <div
              class="prototype-bar-fill"
              :style="{ height: `${barHeight(hour.score)}%` }"
            ></div>
          </div>
        </div>

        <div class="prototype-hour-labels" aria-hidden="true">
          <span v-for="(hour, index) in hourlyForecast" :key="`label-${hour.hour}-${index}`">
            {{ formatShortHour(hour.hour) }}
          </span>
        </div>

        <div class="prototype-legend">
          <div class="legend-item good">
            <span></span>
            Good
          </div>
          <div class="legend-item moderate">
            <span></span>
            Moderate
          </div>
          <div class="legend-item high">
            <span></span>
            High risk
          </div>
          <div class="legend-item best">
            <span></span>
            Best window
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps({
  factors: {
    type: Array,
    default: () => [],
  },
  bestTimeData: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: [String, Error, null],
    default: null,
  },
  suburb: {
    type: String,
    default: 'Melbourne',
  },
  hours: {
    type: Number,
    default: 12,
  },
  autoFetch: {
    type: Boolean,
    default: true,
  },
})

const internalData = ref(null)
const internalLoading = ref(false)
const internalError = ref(null)

const API_BASE = (
  import.meta.env.VITE_ASTHMASAFE_API_BASE ||
  import.meta.env.VITE_API_BASE ||
  'https://asthmasafe-api.onrender.com'
).replace(/\/$/, '')

const clamp = (num, min, max) => Math.min(Math.max(num, min), max)

async function fetchBestTime() {
  if (!props.autoFetch || props.bestTimeData) return

  internalLoading.value = true
  internalError.value = null

  try {
    const url = `${API_BASE}/api/best-time?suburb=${encodeURIComponent(props.suburb)}&hours=${props.hours}`
    const response = await fetch(url)
    const payload = await response.json()

    if (!response.ok || !payload.success) {
      throw new Error(payload.error || `Best-time API failed: ${response.status}`)
    }

    internalData.value = payload
  } catch (error) {
    internalError.value = error
    console.error('Failed to load best-time forecast', error)
  } finally {
    internalLoading.value = false
  }
}

onMounted(fetchBestTime)

watch(
  () => [props.suburb, props.hours, props.bestTimeData],
  () => fetchBestTime()
)

const apiData = computed(() => props.bestTimeData || internalData.value)
const isLoading = computed(() => props.loading || internalLoading.value)
const displayError = computed(() => props.error || internalError.value)

const factorValueToNumber = (value = '') => {
  const match = String(value).match(/-?\d+(\.\d+)?/)
  return match ? Number(match[0]) : 0
}

const normaliseFactorMap = computed(() => {
  const map = {
    pm25: 0,
    pm10: 0,
    ozone: 0,
    no2: 0,
  }

  for (const factor of props.factors) {
    const title = String(factor.title || factor.name || factor.label || '').toLowerCase()
    const numeric = factorValueToNumber(factor.value)

    if (title.includes('pm2.5') || title.includes('pm25')) map.pm25 = numeric
    else if (title.includes('pm10')) map.pm10 = numeric
    else if (title.includes('ozone') || title.includes('o3')) map.ozone = numeric
    else if (title.includes('no2') || title.includes('nitrogen')) map.no2 = numeric
  }

  return map
})

const scorePm25 = (v) => {
  if (v <= 8) return 18
  if (v <= 15) return 32
  if (v <= 25) return 50
  return 72
}

const scorePm10 = (v) => {
  if (v <= 20) return 10
  if (v <= 35) return 20
  if (v <= 50) return 32
  return 45
}

const scoreOzone = (v) => {
  if (v <= 30) return 10
  if (v <= 60) return 20
  if (v <= 100) return 32
  return 45
}

const scoreNo2 = (v) => {
  if (v <= 25) return 8
  if (v <= 50) return 16
  if (v <= 100) return 28
  return 40
}

const hourAdjustment = (hour) => {
  if (hour >= 6 && hour <= 9) return -10
  if (hour >= 10 && hour <= 12) return -4
  if (hour >= 13 && hour <= 16) return 8
  if (hour >= 17 && hour <= 19) return 3
  return 6
}

const scoreToLevel = (score) => {
  if (score <= 25) return 'Low'
  if (score <= 50) return 'Moderate'
  if (score <= 75) return 'High'
  return 'Very High'
}

const baseScore = computed(() => {
  const f = normaliseFactorMap.value
  const raw =
    scorePm25(f.pm25) +
    scorePm10(f.pm10) +
    scoreOzone(f.ozone) +
    scoreNo2(f.no2)

  return clamp(Math.round(raw / 2), 0, 100)
})

const fallbackHourlyForecast = computed(() => {
  const currentHour = new Date().getHours()
  const hours = []

  for (let i = 0; i < props.hours; i += 1) {
    const hour = (currentHour + i) % 24
    const score = clamp(baseScore.value + hourAdjustment(hour), 0, 100)

    hours.push({
      hour,
      score,
      level: scoreToLevel(score),
    })
  }

  return hours
})

const hourlyForecast = computed(() => {
  const apiForecast = apiData.value?.hourly_forecast

  if (Array.isArray(apiForecast) && apiForecast.length) {
    return apiForecast.slice(0, props.hours).map((item) => ({
      hour: Number(item.hour),
      time: item.time,
      score: Number(item.overall_score ?? item.score ?? 0),
      level: item.overall_level || item.level || scoreToLevel(Number(item.overall_score ?? item.score ?? 0)),
      dustScore: item.dust_score,
      dustLevel: item.dust_level,
      aqi: item.aqi,
      aqiLevel: item.aqi_level,
      predictedPm10: item.predicted_pm10,
      baselinePm10: item.baseline_pm10,
      dustContribution: item.dust_contribution,
    }))
  }

  return fallbackHourlyForecast.value
})

const bestTime = computed(() => {
  const apiBest = apiData.value?.best_time

  if (apiBest) {
    return {
      hour: Number(apiBest.hour),
      time: apiBest.time,
      score: Number(apiBest.score ?? 0),
      level: apiBest.level || scoreToLevel(Number(apiBest.score ?? 0)),
      message: apiBest.message,
    }
  }

  return [...hourlyForecast.value].sort((a, b) => a.score - b.score)[0] || {
    hour: null,
    score: 0,
    level: 'Unknown',
  }
})

const bestTimeReason = computed(() => {
  if (apiData.value?.best_time?.message) {
    const scoreText = bestTime.value.score ? `Risk is ${bestTime.value.level} (${bestTime.value.score}/100)` : ''
    return scoreText || apiData.value.best_time.message
  }

  const level = bestTime.value.level

  if (level === 'Low') {
    return 'Ideal for outdoor play or a school run'
  }
  if (level === 'Moderate') {
    return 'Better than nearby hours, with a little extra care'
  }
  return 'Best available window, but keep outdoor time shorter'
})

function isBestHour(hour) {
  return Number(hour.hour) === Number(bestTime.value.hour)
}

function formatHour(h) {
  if (h === null || h === undefined || Number.isNaN(Number(h))) return '--'
  const hour = Number(h)
  const period = hour < 12 ? 'am' : 'pm'
  const display = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour
  return `${display}${period}`
}

function formatShortHour(h) {
  if (h === null || h === undefined || Number.isNaN(Number(h))) return '--'
  const hour = Number(h)
  const display = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour
  return `${display}`
}

function levelClass(level) {
  const lower = String(level || '').toLowerCase()
  if (lower.includes('very')) return 'veryhigh'
  if (lower.includes('high')) return 'high'
  if (lower.includes('moderate')) return 'moderate'
  if (lower.includes('low')) return 'low'
  return 'unknown'
}

function barHeight(score) {
  return clamp(112 - Number(score || 0) * 0.45, 62, 100)
}

function riskLabel(level) {
  const lower = String(level || '').toLowerCase()
  if (lower.includes('low')) return 'Good'
  if (lower.includes('moderate')) return 'Moderate'
  return 'High risk'
}
</script>

<style scoped>
.best-time-section {
  background: var(--bg-cream, #faf7f2);
  padding: 72px 0 78px;
  overflow: hidden;
}

.best-time-inner {
  width: min(1120px, calc(100% - 48px));
  margin: 0 auto;
}

.best-time-content {
  max-width: 980px;
  margin: 0 auto;
}

.timing-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  color: #9b6f0f;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.timing-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #9b6f0f;
}

.best-time-headline-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 52px;
  align-items: start;
  margin-bottom: 30px;
}

.best-time-copy h2 {
  margin: 0;
  color: #142b27;
  font-family: var(--font-serif, Georgia, serif);
  font-size: clamp(40px, 4.8vw, 58px);
  font-weight: 600;
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.best-time-copy p {
  max-width: 570px;
  margin: 24px 0 0;
  color: #6f8a86;
  font-size: 17px;
  line-height: 1.65;
}

.best-window {
  padding-top: 30px;
  text-align: center;
}

.best-window p {
  margin: 0 0 8px;
  color: #6f8a86;
  font-size: 14px;
  font-weight: 600;
}

.best-window strong {
  display: block;
  color: #9b6f0f;
  font-family: var(--font-serif, Georgia, serif);
  font-size: clamp(58px, 7vw, 78px);
  font-weight: 600;
  line-height: 0.95;
}

.best-window span {
  display: block;
  max-width: 290px;
  margin: 14px auto 0;
  color: #6f8a86;
  font-size: 14px;
  line-height: 1.45;
}

.prototype-chart {
  display: grid;
  grid-template-columns: repeat(12, minmax(42px, 50px));
  justify-content: center;
  align-items: end;
  gap: 10px;
  min-height: 300px;
  max-width: 760px;
  margin: -6px auto 0;
}

.prototype-bar-item {
  position: relative;
  display: flex;
  align-items: end;
  height: 300px;
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.55s cubic-bezier(0.16, 1, 0.3, 1), transform 0.55s cubic-bezier(0.16, 1, 0.3, 1);
}

.best-time-section.visible .prototype-bar-item,
.best-time-section.reveal.visible .prototype-bar-item,
.prototype-bar-item {
  opacity: 1;
  transform: translateY(0);
}

.prototype-bar-fill {
  width: 100%;
  min-height: 165px;
  border-radius: 12px 12px 0 0;
  background: rgba(156, 198, 191, 0.88);
  transition: height 0.35s ease, transform 0.22s ease, box-shadow 0.22s ease;
}

.prototype-bar-item:hover .prototype-bar-fill {
  transform: translateY(-4px);
}

.prototype-bar-item.low .prototype-bar-fill {
  background: rgba(156, 198, 191, 0.88);
}

.prototype-bar-item.moderate .prototype-bar-fill {
  background: rgba(231, 194, 165, 0.9);
}

.prototype-bar-item.high .prototype-bar-fill,
.prototype-bar-item.veryhigh .prototype-bar-fill {
  background: rgba(225, 166, 164, 0.92);
}

.prototype-bar-item.active .prototype-bar-fill {
  background: #23968b;
  border: 2px solid #d48a39;
  box-shadow: 0 0 0 3px rgba(212, 138, 57, 0.13);
}

.prototype-hour-labels {
  display: grid;
  grid-template-columns: repeat(12, minmax(42px, 50px));
  justify-content: center;
  gap: 10px;
  max-width: 760px;
  margin: 8px auto 0;
}

.prototype-hour-labels span {
  color: #6f8a86;
  font-size: 12px;
  text-align: center;
}

.prototype-legend {
  display: flex;
  justify-content: center;
  gap: 34px;
  flex-wrap: wrap;
  margin-top: 22px;
  color: #6f8a86;
  font-size: 14px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 9px;
}

.legend-item span {
  width: 13px;
  height: 13px;
  border-radius: 4px;
  display: inline-block;
}

.legend-item.good span {
  background: #23968b;
}

.legend-item.moderate span {
  background: #d88445;
}

.legend-item.high span {
  background: #cf4545;
}

.legend-item.best span {
  border: 2px solid #a87610;
  background: transparent;
}

@media (max-width: 900px) {
  .best-time-headline-row {
    grid-template-columns: 1fr;
    gap: 22px;
    margin-bottom: 28px;
  }

  .best-window {
    padding-top: 0;
    text-align: left;
  }

  .best-window span {
    margin-left: 0;
    margin-right: 0;
  }
}

@media (max-width: 720px) {
  .best-time-section {
    padding: 68px 0 78px;
  }

  .best-time-inner {
    width: min(100% - 32px, 1120px);
  }

  .prototype-chart,
  .prototype-hour-labels {
    grid-template-columns: repeat(12, minmax(24px, 34px));
    justify-content: flex-start;
    gap: 6px;
    overflow-x: auto;
  }

  .prototype-bar-item {
    min-width: 24px;
    height: 270px;
  }

  .prototype-bar-fill {
    min-height: 130px;
    border-radius: 10px 10px 0 0;
  }

  .prototype-legend {
    justify-content: flex-start;
    gap: 18px;
  }
}
</style>
