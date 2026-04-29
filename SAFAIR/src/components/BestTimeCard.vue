<template>
  <article class="card best-time-card reveal">
    <div class="best-time-header">
      <div>
        <span class="eyebrow timing-eyebrow">Timing matters</span>
        <h2 class="section-title">Best time to go outside today</h2>
        <p class="muted">
          Air quality varies throughout the day. Here is when conditions are best
          for outdoor activities.
        </p>
      </div>
    </div>

    <div class="best-time-grid">
      <div class="best-panel">
        <p class="panel-label">Best time today</p>
        <h3>{{ formatHour(bestTime.hour) }}</h3>

        <span class="condition-pill" :class="levelClass(bestTime.level)">
          {{ bestTime.level }} conditions
        </span>

        <p class="best-reason">{{ bestTimeReason }}</p>

        <div class="comparison-heading">
          Hourly comparison <span>({{ periodLabel }})</span>
        </div>

        <div class="bar-chart" role="img" aria-label="Hourly air quality comparison">
          <div
            v-for="(hour, index) in hourlyForecast"
            :key="hour.hour"
            class="bar-item"
            :class="{ active: hour.hour === bestTime.hour }"
            :style="{ transitionDelay: `${index * 0.06}s` }"
          >
            <div class="bar-wrap">
              <div
                class="bar-fill"
                :style="{ height: `${barHeight(hour.score)}%` }"
              ></div>
            </div>
            <span>{{ formatShortHour(hour.hour) }}</span>
          </div>
        </div>
      </div>

      <aside class="how-card">
        <h3>How it works</h3>

        <div class="how-steps">
          <div v-for="(step, index) in howSteps" :key="step.number" class="how-step"
            :style="{ transitionDelay: `${0.18 + index * 0.06}s` }">
            <span>{{ step.number }}</span>
            <p>{{ step.text }}</p>
          </div>
        </div>
</aside>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  factors: {
    type: Array,
    default: () => [],
  },
})

const howSteps = [
  { number: 1, text: 'We look at key pollutants' },
  { number: 2, text: 'We check the forecast' },
  { number: 3, text: 'We find the gentlest window' },
  { number: 4, text: 'We present it simply' },
]

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

    if (title.includes('pm2.5') || title.includes('pm25')) map.pm25 = numeric
    else if (title.includes('pm10')) map.pm10 = numeric
    else if (title.includes('ozone') || title.includes('o3')) map.ozone = numeric
    else if (title.includes('no2') || title.includes('nitrogen')) map.no2 = numeric
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

  for (let i = 0; i < 7; i += 1) {
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

const bestTime = computed(() =>
  [...hourlyForecast.value].sort((a, b) => a.score - b.score)[0]
)

const bestTimeReason = computed(() => {
  const level = bestTime.value.level

  if (level === 'Low') {
    return 'This is the gentlest window today, so outdoor activity should feel more comfortable.'
  }
  if (level === 'Moderate') {
    return 'This time looks more manageable than the surrounding hours, with a little extra care.'
  }
  if (level === 'High') {
    return 'This is still the better option today, but it is safer to keep outdoor time shorter.'
  }
  return 'Conditions stay difficult across the day, so limiting outdoor activity may be the safer choice.'
})

const periodLabel = computed(() => {
  const hour = bestTime.value.hour
  if (hour >= 5 && hour < 12) return 'Morning'
  if (hour >= 12 && hour < 17) return 'Afternoon'
  if (hour >= 17 && hour < 22) return 'Evening'
  return 'Night'
})

function formatHour(h) {
  if (h === null || h === undefined) return '--'
  const period = h < 12 ? 'AM' : 'PM'
  const display = h === 0 ? 12 : h > 12 ? h - 12 : h
  return `${display}:00 ${period}`
}

function formatShortHour(h) {
  if (h === null || h === undefined) return '--'
  const period = h < 12 ? 'AM' : 'PM'
  const display = h === 0 ? 12 : h > 12 ? h - 12 : h
  return `${display} ${period}`
}

function levelClass(level) {
  if (level === 'Low') return 'low'
  if (level === 'Moderate') return 'moderate'
  if (level === 'High') return 'high'
  if (level === 'Very High') return 'veryhigh'
  return 'unknown'
}

function barHeight(score) {
  return clamp(100 - score + 18, 28, 100)
}
</script>

<style scoped>
.best-time-card {
  margin-bottom: 64px;
  overflow: hidden;
  border: 1px solid rgba(240, 200, 87, 0.26);
  border-radius: var(--radius-xl);
  transition-property: opacity, transform, box-shadow;
}

.best-time-card.visible {
  box-shadow: var(--shadow-soft);
}

.best-time-header {
  padding: 28px 32px 26px;
  background: #fff4dd;
}

.timing-eyebrow {
  color: #c87108;
}

.timing-eyebrow::before {
  background: #c87108;
}

.best-time-header .section-title {
  margin-bottom: 12px;
  font-size: 30px;
}

.best-time-header .muted {
  max-width: 780px;
  margin: 0;
  font-size: 16px;
  line-height: 1.65;
}

.best-time-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(300px, 0.95fr);
  gap: 32px;
  padding: 32px;
}

.best-panel,
.how-card {
  border-radius: var(--radius-lg);
  background: var(--bg-white);
  box-shadow: var(--shadow-card);
  transition: transform 0.24s var(--ease-out-quart), box-shadow 0.24s ease;
}

.best-panel:hover,
.how-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-soft);
}

.best-panel {
  padding: 32px 34px;
}

.panel-label,
.comparison-heading {
  color: #667085;
  font-size: 14px;
  font-weight: 600;
}

.panel-label {
  margin: 0 0 8px;
}

.best-panel h3 {
  margin: 0 0 10px;
  color: var(--primary-dark);
  font-family: var(--font-serif);
  font-size: clamp(42px, 5vw, 54px);
  font-weight: 500;
  line-height: 1;
}

.condition-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  animation: pillIn 0.55s var(--ease-out-expo) both;
}

@keyframes pillIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.condition-pill.low {
  background: var(--teal-light);
  color: #1e7a5b;
}

.condition-pill.moderate {
  background: #f7eadb;
  color: #c87108;
}

.condition-pill.high,
.condition-pill.veryhigh {
  background: #fde7ee;
  color: #cf3859;
}

.best-reason {
  margin: 18px 0 36px;
  max-width: 760px;
  color: var(--text-dark);
  font-size: 17px;
  line-height: 1.65;
}

.comparison-heading {
  margin-bottom: 24px;
}

.comparison-heading span {
  color: #6b7280;
}

.bar-chart {
  display: grid;
  grid-template-columns: repeat(7, minmax(54px, 1fr));
  align-items: end;
  gap: 18px;
  min-height: 220px;
}

.bar-item {
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 10px;
  min-height: 220px;
  text-align: center;
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.5s var(--ease-out-expo), transform 0.5s var(--ease-out-expo);
}

.best-time-card.visible .bar-item {
  opacity: 1;
  transform: translateY(0);
}

.bar-wrap {
  display: flex;
  align-items: end;
  height: 190px;
}

.bar-fill {
  width: 100%;
  min-height: 42px;
  border-radius: var(--radius-xs) var(--radius-xs) 0 0;
  background: rgba(13, 107, 94, 0.68);
  transform-origin: bottom;
  animation: growBar 0.75s var(--ease-out-expo) both;
  transition: height 0.3s var(--ease-out-quart), background 0.2s ease, transform 0.2s ease;
}

.bar-item:hover .bar-fill {
  transform: scaleY(1.03);
}

@keyframes growBar {
  from { transform: scaleY(0.18); opacity: 0.4; }
  to { transform: scaleY(1); opacity: 1; }
}

.bar-item.active .bar-fill {
  background: rgba(102, 161, 115, 0.68);
  box-shadow: 0 0 0 4px rgba(102, 161, 115, 0.1);
}

.bar-item span {
  color: var(--text-muted);
  font-size: 14px;
  white-space: nowrap;
}

.how-card {
  padding: 32px;
}

.how-card h3 {
  margin: 0 0 26px;
  color: var(--primary-dark);
  font-family: var(--font-serif);
  font-size: 30px;
  font-weight: 600;
}

.how-steps {
  display: grid;
  gap: 22px;
  margin-bottom: 32px;
}

.how-step {
  display: grid;
  grid-template-columns: 42px 1fr;
  align-items: center;
  gap: 16px;
  opacity: 0;
  transform: translateX(10px);
  transition: opacity 0.5s var(--ease-out-expo), transform 0.5s var(--ease-out-expo);
}

.best-time-card.visible .how-step {
  opacity: 1;
  transform: translateX(0);
}

.how-step span {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--primary);
  color: var(--text-light);
  font-weight: 700;
  transition: transform 0.2s var(--ease-out-quart), background 0.2s ease;
}

.how-step:hover span {
  transform: scale(1.07);
  background: var(--primary-dark);
}

.how-step p {
  margin: 0;
  color: var(--text-dark);
  font-size: 15px;
  line-height: 1.5;
}

.learn-link {
  width: 100%;
  justify-content: center;
}

@media (prefers-reduced-motion: reduce) {
  .best-time-card,
  .best-panel,
  .how-card,
  .condition-pill,
  .bar-item,
  .bar-fill,
  .how-step,
  .how-step span {
    transition: none;
    animation: none;
  }

  .bar-item,
  .how-step {
    opacity: 1;
    transform: none;
  }
}

@media (max-width: 992px) {
  .best-time-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .best-time-header,
  .best-time-grid,
  .best-panel,
  .how-card {
    padding: 24px;
  }

  .bar-chart {
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 6px;
  }

  .bar-item {
    min-width: 54px;
  }
}
</style>
