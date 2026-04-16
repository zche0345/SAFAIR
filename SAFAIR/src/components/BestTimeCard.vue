<template>
  <div class="best-time-card">
    <div class="section-heading">
      <span class="section-icon" aria-hidden="true">◔</span>
      <h2>Best time to go outside</h2>
    </div>

    <p class="section-subtext">
      We looked at today’s air conditions and compared the next few hours to find
      a gentler time for outdoor activity.
    </p>

    <div class="best-highlight" :class="levelClass(bestTime.level)">
      <div class="best-highlight-icon" :class="levelClass(bestTime.level)" aria-hidden="true">
        <span v-if="bestTime.level === 'Low'">◌</span>
        <span v-else-if="bestTime.level === 'Moderate'">◐</span>
        <span v-else-if="bestTime.level === 'High'">◕</span>
        <span v-else>●</span>
      </div>

      <div class="best-highlight-copy">
        <p class="best-highlight-label">Best time today</p>
        <h3>{{ formatHour(bestTime.hour) }}</h3>
        <p class="best-highlight-note">
          {{ bestTimeReason }}
        </p>
      </div>

      <div class="best-time-pill" :class="levelClass(bestTime.level)">
        {{ bestTime.level }}
      </div>
    </div>

    <div class="forecast-card">
      <div class="forecast-top">
        <h3>How the next few hours compare</h3>
        <p>Lower bars suggest a gentler time for being outside.</p>
      </div>

      <div class="bars">
        <div
          v-for="hour in hourlyForecast"
          :key="hour.hour"
          class="bar-row"
          :class="{ highlight: hour.hour === bestTime.hour }"
        >
          <div class="bar-hour">
            {{ formatHour(hour.hour) }}
          </div>

          <div class="bar-track">
            <div
              class="bar-fill"
              :class="levelClass(hour.level)"
              :style="{ width: `${hour.score}%` }"
            ></div>
          </div>

          <div class="bar-meta">
            <span class="bar-level" :class="levelClass(hour.level)">
              {{ hourExplanation(hour.level) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="best-time-meta">
      <span class="meta-label">What this means</span>
      <span class="meta-value">{{ bestTimeReason }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  factors: {
    type: Array,
    default: () => [],
  },
})

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
    const title = String(factor.title || '').toLowerCase()
    const numeric = factorValueToNumber(factor.value)

    if (title.includes('pm2.5')) map.pm25 = numeric
    else if (title.includes('pm10')) map.pm10 = numeric
    else if (title.includes('ozone')) map.ozone = numeric
    else if (title.includes('no2')) map.no2 = numeric
  }

  return map
})

const currentHour = new Date().getHours()

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
  if (hour >= 6 && hour <= 9) return -18
  if (hour >= 10 && hour <= 12) return -6
  if (hour >= 13 && hour <= 16) return 8
  if (hour >= 17 && hour <= 19) return 2
  return 6
}

const clamp = (num, min, max) => Math.min(Math.max(num, min), max)

const scoreToLevel = (score) => {
  if (score <= 24) return 'Low'
  if (score <= 49) return 'Moderate'
  if (score <= 74) return 'High'
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

const hourlyForecast = computed(() => {
  const hours = []

  for (let i = 0; i < 6; i += 1) {
    const hour = (currentHour + i) % 24
    const adjustedScore = clamp(baseScore.value + hourAdjustment(hour), 0, 100)

    hours.push({
      hour,
      score: adjustedScore,
      level: scoreToLevel(adjustedScore),
    })
  }

  return hours
})

const bestTime = computed(() => {
  return [...hourlyForecast.value].sort((a, b) => a.score - b.score)[0]
})

const bestTimeReason = computed(() => {
  const level = bestTime.value.level

  if (level === 'Low') {
    return 'Air conditions look calmer around this time, so outdoor activity may feel more comfortable.'
  }
  if (level === 'Moderate') {
    return 'This time looks more manageable than the surrounding hours, with a little extra care.'
  }
  if (level === 'High') {
    return 'This is still the better option today, but it would be good to keep outdoor time shorter.'
  }
  return 'Conditions stay more difficult across the day, so limiting outdoor activity may be the safer choice.'
})

function formatHour(h) {
  if (h === null || h === undefined) return '--'
  const period = h < 12 ? 'AM' : 'PM'
  const display = h === 0 ? 12 : h > 12 ? h - 12 : h
  return `${display}:00 ${period}`
}

function levelClass(level) {
  if (level === 'Low') return 'low'
  if (level === 'Moderate') return 'moderate'
  if (level === 'High') return 'high'
  if (level === 'Very High') return 'veryhigh'
  return 'unknown'
}

function hourExplanation(level) {
  if (level === 'Low') return 'Feels gentler'
  if (level === 'Moderate') return 'Mostly okay with care'
  if (level === 'High') return 'May trigger symptoms'
  if (level === 'Very High') return 'Better to avoid'
  return 'Conditions unclear'
}
</script>

<style scoped>
.best-time-card {
  background: white;
  border-radius: 28px;
  box-shadow: var(--shadow-soft);
  padding: 36px 38px;
  margin-bottom: 56px;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.section-heading h2 {
  margin: 0;
  font-size: 32px;
  font-weight: 500;
  color: var(--text-dark);
}

.section-icon {
  color: #ff6c7d;
  font-size: 24px;
  line-height: 1;
}

.section-subtext {
  margin: 0 0 26px;
  color: var(--text-muted);
  font-size: 17px;
  line-height: 1.6;
}

.best-highlight {
  display: flex;
  align-items: center;
  gap: 20px;
  border-radius: 28px;
  padding: 28px 30px;
  margin-bottom: 24px;
  border: 1px solid transparent;
}

.best-highlight.low {
  background: #e4f7ef;
  border-color: #b7ead6;
}

.best-highlight.moderate {
  background: #fbf2dd;
  border-color: #edd18e;
}

.best-highlight.high {
  background: #fde7ee;
  border-color: #f5c7d5;
}

.best-highlight.veryhigh {
  background: #fde2e2;
  border-color: #f3b4b4;
}

.best-highlight.unknown {
  background: #f3f4f6;
  border-color: #d9dee7;
}

.best-highlight-icon {
  width: 72px;
  height: 72px;
  min-width: 72px;
  border-radius: 20px;
  display: grid;
  place-items: center;
  font-size: 30px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
}

.best-highlight-icon.low {
  color: #11915d;
}

.best-highlight-icon.moderate {
  color: #d36c00;
}

.best-highlight-icon.high {
  color: #ea2951;
}

.best-highlight-icon.veryhigh {
  color: #c0392b;
}

.best-highlight-icon.unknown {
  color: #5d6777;
}

.best-highlight-copy {
  flex: 1;
  min-width: 0;
}

.best-highlight-label {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6b7280;
}

.best-highlight-copy h3 {
  margin: 0 0 8px;
  font-size: 42px;
  line-height: 1.05;
  font-weight: 600;
  color: var(--text-dark);
}

.best-highlight-note {
  margin: 0;
  color: #4d5969;
  font-size: 16px;
  line-height: 1.6;
  max-width: 760px;
}

.best-time-pill {
  border-radius: 999px;
  padding: 12px 18px;
  font-size: 15px;
  font-weight: 700;
  white-space: nowrap;
}

.best-time-pill.low {
  background: #ccf0e0;
  border: 1px solid #9be0bf;
  color: #11915d;
}

.best-time-pill.moderate {
  background: #f9ebbe;
  border: 1px solid #f0d35e;
  color: #d36c00;
}

.best-time-pill.high {
  background: #fad9df;
  border: 1px solid #f3c0ca;
  color: #ea2951;
}

.best-time-pill.veryhigh {
  background: #f7d2d2;
  border: 1px solid #efb0b0;
  color: #c0392b;
}

.best-time-pill.unknown {
  background: #eef1f5;
  border: 1px solid #d9dee7;
  color: #5d6777;
}

.forecast-card {
  background: #fafbfc;
  border: 1px solid #eef1f5;
  border-radius: 24px;
  padding: 24px;
}

.forecast-top {
  margin-bottom: 18px;
}

.forecast-top h3 {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-dark);
}

.forecast-top p {
  margin: 0;
  font-size: 15px;
  color: var(--text-muted);
}

.bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-row {
  display: grid;
  grid-template-columns: 92px 1fr 160px;
  gap: 14px;
  align-items: center;
  padding: 8px 10px;
  border-radius: 12px;
}

.bar-row.highlight {
  background: #fff9e8;
  border: 1px solid #f3df9a;
}

.bar-hour {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
}

.bar-track {
  height: 16px;
  border-radius: 999px;
  overflow: hidden;
  background: #eceff3;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
}

.bar-fill.low {
  background: #29c45a;
}

.bar-fill.moderate {
  background: #eab308;
}

.bar-fill.high {
  background: #f97316;
}

.bar-fill.veryhigh {
  background: #ef4444;
}

.bar-fill.unknown {
  background: #9ca3af;
}

.bar-meta {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 10px;
}

.bar-level {
  font-size: 14px;
  font-weight: 600;
}

.bar-level.low {
  color: #11915d;
}

.bar-level.moderate {
  color: #d36c00;
}

.bar-level.high {
  color: #ea2951;
}

.bar-level.veryhigh {
  color: #c0392b;
}

.bar-level.unknown {
  color: #6b7280;
}

.best-time-meta {
  margin-top: 18px;
  padding: 14px 18px;
  background: #f9fafb;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.meta-label {
  color: #6b7280;
  font-size: 14px;
  font-weight: 600;
}

.meta-value {
  color: var(--text-dark);
  font-size: 15px;
  font-weight: 500;
  line-height: 1.6;
  flex: 1;
  text-align: right;
}

@media (max-width: 768px) {
  .best-time-card {
    padding: 24px;
  }

  .section-heading h2 {
    font-size: 26px;
  }

  .best-highlight {
    flex-direction: column;
    align-items: flex-start;
  }

  .best-highlight-copy h3 {
    font-size: 34px;
  }

  .best-time-pill {
    align-self: flex-start;
  }

  .bar-row {
    grid-template-columns: 78px 1fr;
    gap: 10px;
  }

  .bar-meta {
    grid-column: 1 / -1;
    padding-left: 0;
  }

  .best-time-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .meta-value {
    text-align: left;
  }
}
</style>