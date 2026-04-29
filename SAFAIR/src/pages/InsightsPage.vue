<template>
  <div class="insights-page">
    <div class="scroll-progress" :style="{ transform: `scaleX(${scrollProgress})` }" aria-hidden="true"></div>
    <section class="insights-hero">
      <div class="container insights-hero-grid">
        <div class="insights-hero-copy reveal">
          <router-link to="/" class="back-link">← Back to Home</router-link>

          <h1>
            What is in Melbourne<br />
            <span>air today?</span>
          </h1>

          <p>{{ heroDateText }}</p>
        </div>

        <div class="hero-image-wrap reveal reveal-delay-1" aria-hidden="true">
          <img
            src="../assets/images/insights-action-bg.jpg"
            alt="Child outdoors in clean air"
            class="hero-image"
          />        </div>      </div>
    </section>

    <section class="section insights-content">
      <div class="container">
        <article class="card summary-card reveal">
          <div class="summary-icon" aria-hidden="true">✓</div>

          <div class="summary-text">
            <h2>{{ summaryTitle }}</h2>
            <p v-if="isOffline && usingCachedInsights" class="offline-label">
              You're offline — showing the latest saved insight.
            </p>
            <p>{{ summaryText }}</p>
          </div>

          <span class="risk-pill" :class="summaryLevelClass">
            <span></span>
            {{ summaryLevelLabel }}
          </span>
        </article>

        <div class="monitoring-heading reveal reveal-delay-1">
          <h2 class="section-title">What we are monitoring</h2>
        </div>

        <div ref="monitoringSection" class="factors-list">
          <article
            v-for="(factor, index) in displayFactors"
            :key="factor.title"
            class="card factor-card factor-card-animate"
            :style="{ animationDelay: `${Math.min(index, 4) * 0.08}s` }"
          >
            <div class="factor-main">
              <div class="factor-icon" aria-hidden="true">{{ factor.icon }}</div>

              <div class="factor-title-group">
                <h3>{{ factor.title }}</h3>
                <p>{{ factor.status }}</p>
              </div>

              <span class="factor-value-pill">
                <span></span>
                {{ factor.value }}
              </span>
            </div>

            <div class="factor-divider"></div>

            <p class="factor-description">{{ factor.description }}</p>

            <button class="factor-toggle" @click="toggleFactor(factor.title)">
              Why does this matter?
              <span :class="{ open: openFactor === factor.title }">▼</span>
            </button>

            <transition name="fade">
              <p v-if="openFactor === factor.title" class="factor-extra">
                {{ factor.explanation }}
              </p>
            </transition>
          </article>
        </div>

        <BestTimeCard :factors="displayFactors" />
      </div>
    </section>
  </div>
</template>

<script setup>
import BestTimeCard from '../components/BestTimeCard.vue'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

const INSIGHTS_CACHE_KEY = 'safair_insights_cache_v1'

const openFactor = ref(null)
const scrollProgress = ref(0)
const monitoringSection = ref(null)
let revealObserver = null
const summaryTitle = ref('Good news — Low Risk Today')
const summaryText = ref(
  'Air quality conditions in Melbourne are excellent for outdoor activities. All monitored factors are within safe ranges. This is a great day for park visits, outdoor sports, and walking to school.'
)
const isOffline = ref(false)
const usingCachedInsights = ref(false)

const toggleFactor = (title) => {
  openFactor.value = openFactor.value === title ? null : title
}

const updateScrollProgress = () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight
  scrollProgress.value = maxScroll > 0 ? Math.min(scrollTop / maxScroll, 1) : 0
}

const scrollToMonitoring = () => {
  monitoringSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const setupRevealAnimations = () => {
  const revealEls = document.querySelectorAll('.insights-page .reveal')

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    revealEls.forEach((el) => el.classList.add('visible'))
    return
  }

  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
          revealObserver.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.14, rootMargin: '0px 0px -80px 0px' }
  )

  revealEls.forEach((el) => revealObserver.observe(el))
}

const fallbackFactors = [
  {
    title: 'PM2.5 Particles',
    icon: '💨',
    value: '7.2 µg/m³',
    status: 'Good',
    description: 'Well within safe range for outdoor activities',
    note: 'Well within safe range for outdoor activities',
    explanation:
      'PM2.5 particles are very small particles that can move deep into the lungs. Lower values usually mean breathing feels easier, especially for children with asthma.',
    theme: 'mint',
  },
  {
    title: 'PM10 Particles',
    icon: '🌫️',
    value: '8.1 µg/m³',
    status: 'Good',
    description: 'Minimal particulate matter detected',
    note: 'Minimal particulate matter detected',
    explanation:
      'PM10 includes larger dust and pollen-like particles. These can irritate the throat and airways when levels rise, especially near roads or dusty areas.',
    theme: 'mint',
  },
  {
    title: 'Ozone Level',
    icon: '☀️',
    value: '51 µg/m³',
    status: 'Good',
    description: 'No UV-related ozone concerns',
    note: 'No UV-related ozone concerns',
    explanation:
      'Ozone can build up on warm sunny days and may irritate sensitive airways. Monitoring it helps identify safer times for outdoor activity.',
    theme: 'mint',
  },
  {
    title: 'NO2 Level',
    icon: '🚗',
    value: '9 µg/m³',
    status: 'Low',
    description: 'Traffic emissions are minimal today',
    note: 'Traffic emissions are minimal today',
    explanation:
      'NO2 is commonly linked with traffic pollution. Lower levels mean less irritation risk from vehicle emissions around busy streets.',
    theme: 'mint',
  },
]

const factors = ref([...fallbackFactors])

const displayFactors = computed(() =>
  factors.value.map((factor, index) => ({
    ...fallbackFactors[index % fallbackFactors.length],
    ...factor,
    status: factor.status || factor.condition || factor.level || fallbackFactors[index % fallbackFactors.length].status,
    description: factor.description || factor.note || fallbackFactors[index % fallbackFactors.length].description,
  }))
)

const summaryLevelLabel = computed(() => {
  const title = summaryTitle.value.toLowerCase()
  if (title.includes('very high')) return 'Very High Risk'
  if (title.includes('high')) return 'High Risk'
  if (title.includes('moderate')) return 'Moderate Risk'
  return 'Low Risk'
})

const summaryLevelClass = computed(() => {
  if (summaryLevelLabel.value.includes('Very High')) return 'veryhigh'
  if (summaryLevelLabel.value.includes('High')) return 'high'
  if (summaryLevelLabel.value.includes('Moderate')) return 'moderate'
  return 'low'
})

const heroDateText = computed(() => {
  const today = new Date()
  const formatted = today.toLocaleDateString('en-AU', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })

  return `Real-time air quality analysis for ${formatted}`
})

const buildInsightsUrl = () => {
  const baseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    'https://d204zergykc1k6.cloudfront.net'
  return `${baseUrl.replace(/\/$/, '')}/v1/insights?location=melbourne`
}

const normalizeInsightsPayload = (payload = {}) => ({
  summaryTitle: payload.summaryTitle || 'Good news — Low Risk Today',
  summaryText:
    payload.summaryText ||
    'Air quality conditions in Melbourne are excellent for outdoor activities. All monitored factors are within safe ranges. This is a great day for park visits, outdoor sports, and walking to school.',
  factors:
    Array.isArray(payload.factors) && payload.factors.length
      ? payload.factors
      : fallbackFactors,
})

const readCachedInsights = () => {
  try {
    const raw = localStorage.getItem(INSIGHTS_CACHE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const writeCachedInsights = (payload) => {
  try {
    localStorage.setItem(INSIGHTS_CACHE_KEY, JSON.stringify(payload))
  } catch {
    // Ignore storage write errors.
  }
}

const loadInsights = async () => {
  if (!navigator.onLine) {
    const cached = readCachedInsights()
    if (cached) {
      const normalized = normalizeInsightsPayload(cached)
      summaryTitle.value = normalized.summaryTitle
      summaryText.value = normalized.summaryText
      factors.value = normalized.factors
      usingCachedInsights.value = true
    }
    isOffline.value = true
    return
  }

  try {
    const response = await fetch(buildInsightsUrl())
    if (!response.ok) throw new Error(`Insights API failed: ${response.status}`)

    const payload = await response.json()
    const normalized = normalizeInsightsPayload(payload)

    summaryTitle.value = normalized.summaryTitle
    summaryText.value = normalized.summaryText
    factors.value = normalized.factors
    writeCachedInsights(payload)
    isOffline.value = false
    usingCachedInsights.value = false
  } catch (error) {
    const cached = readCachedInsights()
    if (cached) {
      const normalized = normalizeInsightsPayload(cached)
      summaryTitle.value = normalized.summaryTitle
      summaryText.value = normalized.summaryText
      factors.value = normalized.factors
      usingCachedInsights.value = true
    }
    isOffline.value = !navigator.onLine
    console.error('Failed to load insights', error)
  }
}

onMounted(async () => {
  loadInsights()
  await nextTick()
  setupRevealAnimations()
  updateScrollProgress()
  window.addEventListener('scroll', updateScrollProgress, { passive: true })
})

onBeforeUnmount(() => {
  revealObserver?.disconnect()
  window.removeEventListener('scroll', updateScrollProgress)
})
</script>

<style scoped>
.insights-page {
  min-height: 100vh;
  background: var(--bg-page);
  overflow-x: hidden;
}

.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 60;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, var(--primary), #36bca4);
  box-shadow: 0 0 18px rgba(13, 107, 94, 0.22);
  transform-origin: left;
  transform: scaleX(0);
  transition: transform 0.12s linear;
}

.insights-hero {
  position: relative;
  background: linear-gradient(135deg, var(--teal-deep), #0d8c79 52%, #36bca4);
  padding: 86px 0 100px;
}

.scroll-cue {
  position: absolute;
  left: 50%;
  bottom: 22px;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border: 0;
  background: transparent;
  color: rgba(255, 255, 255, 0.78);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transform: translateX(-50%);
}

.scroll-cue-line {
  width: 1px;
  height: 34px;
  background: rgba(255, 255, 255, 0.72);
  animation: scrollPulse 1.8s ease-in-out infinite;
}

@keyframes scrollPulse {
  0%, 100% { transform: scaleY(0.45); opacity: 0.45; }
  50% { transform: scaleY(1); opacity: 1; }
}

.insights-hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 0.95fr);
  align-items: center;
  gap: 72px;
}

.back-link {
  display: inline-flex;
  margin-bottom: 28px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 17px;
  font-weight: 500;
  transition: transform 0.2s var(--ease-out-quart), opacity 0.2s ease;
}

.back-link:hover {
  transform: translateX(-4px);
  opacity: 0.82;
}

.insights-hero-copy h1 {
  margin: 0 0 24px;
  color: var(--text-light);
  font-family: var(--font-serif);
  font-size: clamp(46px, 5.8vw, 74px);
  font-weight: 500;
  line-height: 1.03;
}

.insights-hero-copy h1 span {
  font-style: italic;
}

.insights-hero-copy p {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
  line-height: 1.7;
}

.hero-image-wrap {
  position: relative;
  overflow: hidden;
  transform: translateZ(0);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-hover);
  min-height: 250px;
}

.hero-image {
  width: 100%;
  height: 100%;
  min-height: 250px;
  object-fit: cover;
  transition: transform 0.7s var(--ease-out-expo);
}

.hero-image-wrap:hover .hero-image {
  transform: scale(1.045);
}

.insights-floating-art {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: grid;
  place-items: center;
}

.insights-art-emoji {
  position: relative;
  z-index: 2;
  font-size: 42px;
  filter: drop-shadow(0 16px 28px rgba(0, 0, 0, 0.22));
  animation: floatInsightIcon 4.6s ease-in-out infinite;
}

.insights-art-orb {
  position: absolute;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.13);
  backdrop-filter: blur(2px);
}

.insights-art-orb-one {
  width: 210px;
  height: 130px;
  transform: rotate(-8deg);
}

.insights-art-orb-two {
  width: 124px;
  height: 92px;
  right: 46px;
  bottom: 44px;
}

@keyframes floatInsightIcon {
  0%, 100% { transform: translateY(0) rotate(-1deg); }
  50% { transform: translateY(-12px) rotate(2deg); }
}

.insights-content {
  padding-top: 0;
}

.insights-hero .container,
.insights-content .container {
  width: min(calc(100% - 160px), 1364px);
}


.summary-card {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr) auto;
  align-items: center;
  gap: 26px;
  margin-top: -42px;
  margin-bottom: 64px;
  padding: 32px;
  border-radius: var(--radius-xl);
}

.summary-icon {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  background: var(--teal-light);
  color: var(--text-dark);
  font-size: 42px;
  line-height: 1;
}

.summary-text h2 {
  margin: 0 0 10px;
  font-family: var(--font-serif);
  font-size: 31px;
  font-weight: 500;
  color: var(--text-dark);
}

.summary-text p {
  margin: 0;
  max-width: 940px;
  color: #394860;
  font-size: 16px;
  line-height: 1.7;
}

.offline-label {
  margin-bottom: 8px;
  color: var(--alert-eyebrow);
  font-weight: 700;
}

.risk-pill,
.factor-value-pill {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  border-radius: 999px;
  background: var(--teal-light);
  color: #1e7a5b;
  font-weight: 600;
  white-space: nowrap;
}

.risk-pill {
  padding: 11px 18px;
}

.risk-pill span,
.factor-value-pill span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.risk-pill.moderate {
  background: #fbf2dd;
  color: #c87108;
}

.risk-pill.high,
.risk-pill.veryhigh {
  background: #fde7ee;
  color: #cf3859;
}

.monitoring-heading {
  margin-bottom: 24px;
}

.monitoring-heading .section-title {
  margin-bottom: 0;
  font-size: 30px;
}

.factors-list {
  display: grid;
  gap: 18px;
  margin-bottom: 64px;
}

.factor-card {
  padding: 24px 26px;
  min-height: 184px;
  border: 1px solid rgba(15, 31, 26, 0.09);
  border-radius: var(--radius-md);
  box-shadow: none;
  background: rgba(255, 255, 255, 0.78);
  transition: transform 0.24s var(--ease-out-quart), box-shadow 0.24s ease, border-color 0.24s ease;
}

.factor-card-animate {
  animation: factorCardIn 0.55s var(--ease-out-expo) both;
}

@keyframes factorCardIn {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.factor-card:hover {
  transform: translateY(-3px);
  border-color: rgba(13, 107, 94, 0.18);
  box-shadow: var(--shadow-card);
}

.factor-card:hover .factor-icon {
  transform: scale(1.05);
}

.factor-main {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
}

.factor-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  display: grid;
  place-items: center;
  background: var(--teal-light);
  font-size: 21px;
  line-height: 1;
  transition: transform 0.24s var(--ease-out-quart);
}

.factor-title-group h3 {
  margin: 0 0 6px;
  color: #202636;
  font-size: 17px;
  font-weight: 700;
}

.factor-title-group p,
.factor-description,
.factor-extra {
  color: #394860;
}

.factor-title-group p {
  margin: 0;
  font-size: 14px;
}

.factor-value-pill {
  padding: 10px 16px;
  font-size: 15px;
}

.factor-divider {
  height: 1px;
  margin: 18px 0 14px;
  background: rgba(15, 31, 26, 0.09);
}

.factor-description {
  margin: 0 0 10px;
  font-size: 15px;
  line-height: 1.6;
}

.factor-toggle {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 0;
  padding: 0;
  background: transparent;
  color: var(--primary-teal);
  font-weight: 700;
  font-size: 15px;
  transition: color 0.2s ease, transform 0.2s ease;
}

.factor-toggle:hover {
  color: var(--primary-dark);
  transform: translateX(2px);
}

.factor-toggle span {
  transition: transform 0.2s ease;
}

.factor-toggle span.open {
  transform: rotate(180deg);
}

.factor-extra {
  margin: 12px 0 0;
  max-width: 900px;
  font-size: 15px;
  line-height: 1.7;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.24s ease, transform 0.24s var(--ease-out-quart);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (prefers-reduced-motion: reduce) {
  .scroll-progress,
  .hero-image,
  .factor-card,
  .factor-card-animate,
  .factor-icon,
  .factor-toggle,
  .scroll-cue-line {
    transition: none;
    animation: none;
  }
}

@media (max-width: 992px) {
  .insights-hero .container,
  .insights-content .container {
    width: min(calc(100% - 32px), var(--container-width));
  }

  .insights-hero-grid {
    grid-template-columns: 1fr;
    gap: 38px;
  }

  .summary-card {
    grid-template-columns: 64px 1fr;
  }

  .risk-pill {
    grid-column: 2;
    justify-self: start;
  }
}

@media (max-width: 768px) {
  .insights-hero {
    padding: 56px 0 82px;
  }

  .summary-card,
  .factor-main {
    grid-template-columns: 1fr;
  }

  .summary-card,
  .factor-card {
    padding: 24px;
  }

  .summary-text h2 {
    font-size: 26px;
  }

  .factor-value-pill {
    justify-self: start;
  }
}
</style>

<style scoped>
.insights-floating-art,
.scroll-cue {
  display: none !important;
}

.hero-image-wrap {
  animation: insightsImageFloat 6s ease-in-out infinite;
  will-change: transform;
}

@keyframes insightsImageFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-12px) rotate(0.35deg); }
}

@media (prefers-reduced-motion: reduce) {
  .hero-image-wrap { animation: none; }
}
</style>
