<template>
  <section id="today" class="section today-section">
    <div class="container">
      <div class="today-heading">
        <span class="heart">♡</span>
        <h2>Today in Melbourne</h2>
      </div>

      <div class="risk-banner">
        <div>
          <p class="eyebrow banner-eyebrow">{{ home.liveUpdateText }}</p>
          <h3>{{ home.statusTitle }}</h3>
          <p v-if="isOffline && usingCachedReading" class="offline-label">
            You're offline
          </p>
          <p v-if="home.isDelayed" class="delayed-label">Data may be delayed</p>
          <p class="banner-text">
            {{ home.statusSummary }}
          </p>
        </div>

        <div class="warning-icon">⚠</div>
      </div>

      <div class="info-grid">
        <article class="info-card card">
          <div class="image-wrap">
            <img src="../assets/images/air-quality.jpg" alt="Air quality" />
            <span class="image-badge amber">☁</span>
          </div>
          <div class="info-content">
            <h4>Air Quality: {{ home.aqiLabel }}</h4>
            <p>
              Current AQI is {{ home.aqi }}. {{ airQualityDescription }}
            </p>
          </div>
        </article>

        <article class="info-card card">
          <div class="image-wrap">
            <img src="../assets/images/pollen.jpeg" alt="Pollen level" />
            <span class="image-badge pink">≋</span>
          </div>
          <div class="info-content">
            <h4>Pollen: High</h4>
            <p>
              Grass pollen is particularly high. Consider keeping windows closed
              between 11am–3pm.
            </p>
          </div>
        </article>
      </div>

      <div class="stats-grid">
        <div class="stat-card mint">
          <span class="stat-label">Temperature</span>
          <strong>{{ home.weather.temperatureC }}°C</strong>
        </div>

        <div class="stat-card mint">
          <span class="stat-label">Humidity</span>
          <strong>{{ home.weather.humidityPct }}%</strong>
        </div>

        <div class="stat-card mint">
          <span class="stat-label">Wind</span>
          <strong>{{ home.weather.windLabel }}</strong>
        </div>

        <div class="stat-card uv">
          <span class="stat-label">UV Index</span>
          <strong>{{ home.weather.uvIndex }}</strong>
        </div>
      </div>

      <div class="plan-card card">
        <div class="plan-header">
          <h3>Best Time to Go Outside</h3>
          <strong>{{ outdoorPlan.bestWindowLabel }}</strong>
        </div>

        <div class="plan-grid">
          <div
            v-for="window in outdoorPlan.windows"
            :key="window.label"
            class="plan-item"
          >
            <span class="plan-time">{{ window.label }}</span>
            <span class="plan-level" :class="levelClass(window.level)">
              {{ window.level }}
            </span>
            <p>{{ window.reason }}</p>
          </div>
        </div>
      </div>

      <div class="action-panel">
        <img
          src="../assets/images/actions-bg.jpeg"
          alt="Background"
          class="action-bg"
        />
        <div class="action-overlay"></div>

        <div class="action-content">
          <h3>What you can do today</h3>

          <ul class="action-list">
            <li
              v-for="(recommendation, index) in visibleRecommendations"
              :key="`${recommendation.level || 'general'}-${recommendation.timeWindow || 'all'}-${index}`"
            >
              <span class="bullet">{{ actionIcons[index % actionIcons.length] }}</span>
              <span class="action-copy">
                <span
                  v-if="recommendation.level && recommendation.level !== 'general'"
                  class="action-level"
                  :class="levelClass(recommendation.level)"
                >
                  {{ recommendation.level }}
                </span>
                {{ recommendation.text }}
              </span>
            </li>
          </ul>

          

          <router-link to="/recommendations" class="btn-pill btn-light action-link">
              See All Recommendations
              <span>→</span>
            </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const HOME_CACHE_KEY = 'safair_home_status_cache_v1'
const OUTDOOR_PLAN_CACHE_KEY = 'safair_outdoor_plan_cache_v1'

const fallbackHome = {
  liveUpdateText: 'Live Update · --:--',
  statusTitle: 'Moderate Asthma Risk',
  statusSummary:
    'Some environmental factors may affect your child today. We recommend a few simple precautions.',
  aqi: '--',
  aqiLabel: 'Moderate',
  isDelayed: false,
  weather: {
    temperatureC: 18,
    humidityPct: 65,
    windLabel: 'Light',
    uvIndex: 6,
  },
  recommendations: [
    "Keep your child's reliever inhaler available when heading out.",
    'Choose lower-intensity outdoor activities when air quality worsens.',
  ],
}

const fallbackOutdoorPlan = {
  bestWindowLabel: 'Best time: 06:00-10:00',
  windows: [
    { label: '06:00-10:00', level: 'safe', reason: 'Lower pollutant levels' },
    { label: '10:00-14:00', level: 'caution', reason: 'Pollutants may rise' },
    { label: '14:00-18:00', level: 'avoid', reason: 'Peak daytime exposure' },
    { label: '18:00-22:00', level: 'safe', reason: 'Conditions usually ease' },
  ],
  dailyRecommendations: [
    {
      level: 'safe',
      timeWindow: '06:00-10:00',
      text: 'Good window for outdoor activity (06:00-10:00). Keep normal precautions and carry the reliever inhaler.',
    },
    {
      level: 'caution',
      timeWindow: '10:00-14:00',
      text: 'Use caution during 10:00-14:00. Keep activities shorter and lower intensity.',
    },
    {
      level: 'avoid',
      timeWindow: '14:00-18:00',
      text: 'Prefer indoor activities during 14:00-18:00. Air conditions may trigger symptoms.',
    },
  ],
}

const home = ref(structuredClone(fallbackHome))
const outdoorPlan = ref(structuredClone(fallbackOutdoorPlan))
const isOffline = ref(false)
const usingCachedReading = ref(false)
const showAllRecommendations = ref(false)
const actionIcons = ['🏠', '🧴', '🌳']

const airQualityDescription = computed(() => {
  if (home.value.aqi === '--') {
    return 'Air quality data is temporarily unavailable.'
  }
  if (home.value.aqi <= 50) {
    return 'Air conditions are generally favorable for outdoor activities.'
  }
  if (home.value.aqi <= 100) {
    return 'Consider shorter outdoor sessions and simple precautions.'
  }
  return 'Prefer indoor activities and reduce strenuous outdoor exposure.'
})

const defaultRecommendations = [
  {
    level: 'caution',
    timeWindow: 'All day',
    text: "Keep your child's reliever inhaler available when heading out.",
  },
  {
    level: 'caution',
    timeWindow: 'All day',
    text: 'Choose lower-intensity outdoor activities when air quality worsens.',
  },
]

const generalRecommendations = computed(() => {
  if (Array.isArray(home.value.recommendations) && home.value.recommendations.length) {
    return home.value.recommendations.slice(0, 2).map((text) => ({
      level: 'general',
      timeWindow: 'All day',
      text,
    }))
  }
  return defaultRecommendations
})

const currentRecommendations = computed(() => {
  if (
    Array.isArray(outdoorPlan.value.dailyRecommendations) &&
    outdoorPlan.value.dailyRecommendations.length
  ) {
    return outdoorPlan.value.dailyRecommendations
  }
  return defaultRecommendations
})

const visibleRecommendations = computed(() =>
  showAllRecommendations.value
    ? currentRecommendations.value
    : generalRecommendations.value
)

const buildHomeUrl = () => {
  const baseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    'https://3z3kc4xlji.execute-api.ap-southeast-2.amazonaws.com'
  return `${baseUrl.replace(/\/$/, '')}/v1/home?location=melbourne`
}

const buildOutdoorPlanUrl = () => {
  const baseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    'https://3z3kc4xlji.execute-api.ap-southeast-2.amazonaws.com'
  return `${baseUrl.replace(/\/$/, '')}/v1/outdoor-plan?location=melbourne`
}

const normalizeHomePayload = (payload) => ({
  ...fallbackHome,
  ...payload,
  weather: {
    ...fallbackHome.weather,
    ...(payload.weather || {}),
  },
  recommendations:
    Array.isArray(payload.recommendations) && payload.recommendations.length
      ? payload.recommendations
      : fallbackHome.recommendations,
})

const readCachedHomeStatus = () => {
  try {
    const raw = localStorage.getItem(HOME_CACHE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

const readCachedOutdoorPlan = () => {
  try {
    const raw = localStorage.getItem(OUTDOOR_PLAN_CACHE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

const writeCachedHomeStatus = (payload) => {
  try {
    localStorage.setItem(HOME_CACHE_KEY, JSON.stringify(payload))
  } catch {
    // Ignore storage write failures.
  }
}

const writeCachedOutdoorPlan = (payload) => {
  try {
    localStorage.setItem(OUTDOOR_PLAN_CACHE_KEY, JSON.stringify(payload))
  } catch {
    // Ignore storage write failures.
  }
}

const normalizeOutdoorPlanPayload = (payload) => ({
  ...fallbackOutdoorPlan,
  ...payload,
  windows:
    Array.isArray(payload.windows) && payload.windows.length
      ? payload.windows
      : fallbackOutdoorPlan.windows,
  dailyRecommendations:
    Array.isArray(payload.dailyRecommendations) && payload.dailyRecommendations.length
      ? payload.dailyRecommendations
      : fallbackOutdoorPlan.dailyRecommendations,
})

const loadHomeStatus = async () => {
  if (!navigator.onLine) {
    const cached = readCachedHomeStatus()
    if (cached) {
      home.value = normalizeHomePayload(cached)
      usingCachedReading.value = true
    }
    isOffline.value = true
    return
  }

  try {
    const response = await fetch(buildHomeUrl())
    if (!response.ok) {
      throw new Error(`Home API failed: ${response.status}`)
    }

    const payload = await response.json()
    home.value = normalizeHomePayload(payload)
    writeCachedHomeStatus(payload)
    isOffline.value = false
    usingCachedReading.value = false
  } catch (error) {
    const cached = readCachedHomeStatus()
    if (cached) {
      home.value = normalizeHomePayload(cached)
      usingCachedReading.value = true
    }
    isOffline.value = !navigator.onLine
    console.error('Failed to load home status', error)
  }
}

const loadOutdoorPlan = async () => {
  if (!navigator.onLine) {
    const cached = readCachedOutdoorPlan()
    if (cached) {
      outdoorPlan.value = normalizeOutdoorPlanPayload(cached)
    }
    return
  }

  try {
    const response = await fetch(buildOutdoorPlanUrl())
    if (!response.ok) {
      throw new Error(`Outdoor plan API failed: ${response.status}`)
    }
    const payload = await response.json()
    outdoorPlan.value = normalizeOutdoorPlanPayload(payload)
    writeCachedOutdoorPlan(payload)
  } catch (error) {
    const cached = readCachedOutdoorPlan()
    if (cached) {
      outdoorPlan.value = normalizeOutdoorPlanPayload(cached)
    }
    console.error('Failed to load outdoor plan', error)
  }
}

const levelClass = (level) => {
  if (level === 'safe') return 'safe'
  if (level === 'avoid') return 'avoid'
  return 'caution'
}

onMounted(() => {
  loadHomeStatus()
  loadOutdoorPlan()
})
</script>

<style scoped>
.today-section {
  background: var(--bg-page);
}

.today-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 22px;
}

.today-heading h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.heart {
  color: #ff6c7d;
  font-size: 22px;
}

.risk-banner {
  background: var(--warning-bg);
  border: 1px solid var(--warning-border);
  border-radius: var(--radius-xl);
  padding: 28px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-bottom: 28px;
  box-shadow: var(--shadow-soft);
}

.banner-eyebrow {
  color: #c66b1f;
  margin: 0 0 10px;
}

.delayed-label {
  margin: 0 0 10px;
  color: #d0642a;
  font-weight: 600;
  font-size: 14px;
}

.offline-label {
  margin: 0 0 10px;
  color: #6d5b19;
  font-weight: 600;
  font-size: 14px;
}

.risk-banner h3 {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 600;
}

.banner-text {
  margin: 0;
  max-width: 680px;
  color: var(--text-muted);
  line-height: 1.65;
}

.warning-icon {
  width: 88px;
  height: 88px;
  min-width: 88px;
  border-radius: 50%;
  background: #f5d97b;
  display: grid;
  place-items: center;
  font-size: 34px;
  box-shadow: var(--shadow-soft);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.info-card {
  overflow: hidden;
}

.image-wrap {
  position: relative;
}

.image-wrap img {
  width: 100%;
  height: 250px;
  object-fit: cover;
}

.image-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: white;
  font-size: 16px;
  font-weight: 700;
}

.image-badge.amber {
  background: #ffad0f;
}

.image-badge.pink {
  background: #ff2e7a;
}

.info-content {
  padding: 22px 22px 24px;
}

.info-content h4 {
  margin: 0 0 12px;
  font-size: 18px;
}

.info-content p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.plan-card {
  padding: 24px;
  margin-bottom: 28px;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 16px;
}

.plan-header h3 {
  margin: 0;
  font-size: 22px;
}

.plan-header strong {
  color: #117f67;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.plan-item {
  border: 1px solid #e4e8ef;
  border-radius: 14px;
  padding: 14px;
  background: #fafcff;
}

.plan-time {
  display: inline-block;
  font-weight: 700;
  margin-bottom: 8px;
}

.plan-level {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  border-radius: 999px;
  padding: 4px 10px;
  margin-left: 8px;
}

.plan-level.safe {
  background: #daf5e8;
  color: #14795f;
}

.plan-level.caution {
  background: #fbeecf;
  color: #9a6215;
}

.plan-level.avoid {
  background: #fbe1e5;
  color: #b23d54;
}

.plan-item p {
  margin: 10px 0 0;
  color: var(--text-muted);
  line-height: 1.5;
}

.stat-card {
  border-radius: 16px;
  padding: 24px 20px;
  text-align: center;
  border: 1px solid rgba(12, 165, 122, 0.16);
}

.stat-card.mint {
  background: #e4f5ee;
}

.stat-card.uv {
  background: var(--uv-bg);
  border-color: rgba(202, 140, 36, 0.18);
}

.stat-label {
  display: block;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #6b7b75;
  margin-bottom: 10px;
  font-weight: 700;
}

.stat-card strong {
  font-size: 30px;
  font-weight: 700;
  color: #117f67;
}

.action-panel {
  position: relative;
  min-height: 340px;
  border-radius: 28px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.action-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.action-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8, 150, 123, 0.92),
    rgba(8, 150, 123, 0.82)
  );
}

.action-content {
  position: relative;
  z-index: 2;
  padding: 34px 32px;
  color: white;
  max-width: 760px;
}

.action-content h3 {
  margin: 0 0 26px;
  font-size: 26px;
  font-weight: 600;
}

.action-list {
  list-style: none;
  padding: 0;
  margin: 0 0 30px;
  display: grid;
  gap: 16px;
}

.action-list li {
  display: flex;
  align-items: center;
  gap: 14px;
  line-height: 1.5;
  font-size: 17px;
}

.action-copy {
  display: inline-block;
}

.action-level {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  border-radius: 999px;
  padding: 3px 8px;
  margin-right: 8px;
}

.bullet {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 12px;
  background: white;
  display: grid;
  place-items: center;
  font-size: 18px;
}

@media (max-width: 992px) {
  .info-grid,
  .stats-grid,
  .plan-grid {
    grid-template-columns: 1fr 1fr;
  }

  .risk-banner {
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .today-heading h2 {
    font-size: 24px;
  }

  .risk-banner {
    flex-direction: column;
    align-items: flex-start;
    padding: 24px;
  }

  .warning-icon {
    width: 72px;
    height: 72px;
    min-width: 72px;
    font-size: 28px;
  }

  .info-grid,
  .stats-grid,
  .plan-grid {
    grid-template-columns: 1fr;
  }

  .image-wrap img {
    height: 220px;
  }

  .action-panel {
    min-height: auto;
  }

  .action-content {
    padding: 28px 22px;
  }

  .action-content h3 {
    font-size: 24px;
  }

  .action-list li {
    align-items: flex-start;
    font-size: 16px;
  }
}
</style>
