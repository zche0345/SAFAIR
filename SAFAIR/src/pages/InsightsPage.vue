<template>
  <div class="insights-page">
    <section class="insights-hero">
      <div class="container">
        <div class="brand-row">
          <div class="brand-left">
            <div class="brand-icon">✦</div>
            <span class="brand-name">SAFAIR</span>
            <router-link to="/" class="back-link">‹ Back to Home</router-link>
          </div>
        </div>

        <div class="hero-copy">
          <h1>What's in Melbourne's air today?</h1>
          <p>Let's understand the conditions affecting your child</p>
        </div>
      </div>
    </section>

    <section class="section insights-content">
      <div class="container">
        <div class="summary-card">
          <div class="summary-icon">⚠</div>
          <div class="summary-text">
            <h2>{{ summaryTitle }}</h2>
            <p v-if="isOffline && usingCachedInsights" class="offline-label">
              You're offline
            </p>
            <p>
              {{ summaryText }}
            </p>
          </div>
        </div>

        <div class="section-heading">
          <span class="heart">♡</span>
          <h2>The factors at play</h2>
        </div>

        <div class="factors-list">
          <article
            v-for="factor in factors"
            :key="factor.title"
            class="factor-card"
            :class="factor.theme"
          >
            <div class="factor-left">
              <div class="factor-icon" :class="factor.theme">
                {{ factor.icon }}
              </div>

              <div class="factor-content">
                <div class="factor-top">
                  <h3>{{ factor.title }}</h3>
                  <span class="factor-badge" :class="factor.theme">
                    {{ factor.value }}
                  </span>
                </div>

                <p class="factor-description">
                  {{ factor.description }}
                </p>

                <p class="factor-note">
                  {{ factor.note }}
                </p>

                <button
                  class="factor-toggle"
                  @click="toggleFactor(factor.title)"
                >
                  Why does this matter?
                  <span
                    class="arrow"
                    :class="{ open: openFactor === factor.title }"
                  >
                    ˅
                  </span>
                </button>

                <transition name="fade">
                  <div
                    v-if="openFactor === factor.title"
                    class="factor-extra"
                  >
                    {{ factor.explanation }}
                  </div>
                </transition>
              </div>
            </div>
          </article>
        </div>

        <BestTimeCard :factors="factors" />

        <div class="action-banner">
          <img
            src="../assets/images/insights-action-bg.jpg"
            alt="Family outdoors"
            class="action-banner-bg"
          />
          <div class="action-banner-overlay"></div>

          <div class="action-banner-content">
            <h2>Ready for action?</h2>
            <p>
              Now that you know what's happening in the air, let's talk about
              practical steps you can take today to keep your child safe and
              comfortable.
            </p>

            <router-link to="/recommendations" class="btn-pill btn-light action-link">
              See What You Can Do
              <span>→</span>
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import BestTimeCard from '../components/BestTimeCard.vue'
import { onMounted, ref } from 'vue'

const INSIGHTS_CACHE_KEY = 'safair_insights_cache_v1'

const openFactor = ref(null)
const summaryTitle = ref('Moderate Risk Today')
const summaryText = ref(
  "A few environmental factors are elevated today. Here's what you should know and simple steps to keep your child comfortable and safe."
)
const isOffline = ref(false)
const usingCachedInsights = ref(false)

const toggleFactor = (title) => {
  openFactor.value = openFactor.value === title ? null : title
}

const fallbackFactors = [
  {
    title: 'PM2.5',
    icon: '☁',
    value: '18 µg/m³',
    description: 'Fine particles in the air are at moderate levels today',
    note: 'May cause mild symptoms during outdoor exercise',
    explanation:
      'Air quality matters because airborne particles can irritate sensitive lungs and make breathing less comfortable, especially during outdoor activity.',
    theme: 'amber',
  },
  {
    title: 'PM10',
    icon: '≋',
    value: '30 µg/m³',
    description: 'Coarse particles are elevated today',
    note: 'Can worsen cough or chest tightness during outdoor time',
    explanation:
      'PM10 can irritate airways and make breathing less comfortable for children with asthma, especially during high-traffic periods.',
    theme: 'pink',
  },
  {
    title: 'Ozone (O3)',
    icon: '◔',
    value: '0.06 ppm',
    description: 'Ozone levels can rise in sunnier afternoon hours',
    note: 'Afternoon outdoor exercise may trigger symptoms',
    explanation:
      'Ozone is a gas pollutant that can inflame sensitive airways. It often gets worse later in the day with stronger sunlight.',
    theme: 'mint',
  },
  {
    title: 'NO2',
    icon: '◍',
    value: '42 ppb',
    description: 'Traffic-related pollution is moderate today',
    note: 'Avoid prolonged time near busy roads where possible',
    explanation:
      'Nitrogen dioxide can increase airway sensitivity. Exposure is often higher near traffic corridors and during congestion.',
    theme: 'amber',
  },
]

const factors = ref([...fallbackFactors])

const buildInsightsUrl = () => {
  const baseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    'https://d204zergykc1k6.cloudfront.net'
  return `${baseUrl.replace(/\/$/, '')}/v1/insights?location=melbourne`
}

const normalizeInsightsPayload = (payload = {}) => ({
  summaryTitle: payload.summaryTitle || 'Moderate Risk Today',
  summaryText:
    payload.summaryText ||
    "A few environmental factors are elevated today. Here's what you should know and simple steps to keep your child comfortable and safe.",
  factors:
    Array.isArray(payload.factors) && payload.factors.length
      ? payload.factors
      : fallbackFactors,
})

const readCachedInsights = () => {
  try {
    const raw = localStorage.getItem(INSIGHTS_CACHE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
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
    if (!response.ok) {
      throw new Error(`Insights API failed: ${response.status}`)
    }

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

onMounted(() => {
  loadInsights()
})
</script>

<style scoped>
.insights-page {
  background: var(--bg-page);
  min-height: 100vh;
}

.insights-hero {
  background: linear-gradient(135deg, var(--primary-teal), var(--primary));
  padding: 56px 0 72px;
}

.brand-row {
  margin-bottom: 44px;
}

.brand-left {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.18);
  display: grid;
  place-items: center;
  font-size: 15px;
}

.brand-name {
  font-size: 18px;
  font-weight: 500;
}

.back-link {
  color: rgba(255, 255, 255, 0.92);
  font-size: 18px;
}

.hero-copy h1 {
  margin: 0 0 20px;
  max-width: 700px;
  font-size: 72px;
  line-height: 1.02;
  font-weight: 400;
  color: white;
}

.hero-copy p {
  margin: 0;
  font-size: 22px;
  color: rgba(255, 255, 255, 0.92);
}

.insights-content {
  padding-top: 56px;
}

.summary-card {
  background: rgba(248, 242, 229, 0.72);
  border: 1px solid #eddca7;
  border-radius: 28px;
  padding: 38px 42px;
  display: flex;
  align-items: center;
  gap: 28px;
  box-shadow: var(--shadow-soft);
  margin-bottom: 64px;
}

.summary-icon {
  width: 100px;
  height: 100px;
  min-width: 100px;
  border-radius: 50%;
  background: #f5d97b;
  display: grid;
  place-items: center;
  font-size: 42px;
  box-shadow: var(--shadow-soft);
}

.summary-text h2 {
  margin: 0 0 14px;
  font-size: 36px;
  font-weight: 500;
}

.summary-text p {
  margin: 0;
  font-size: 18px;
  line-height: 1.7;
  color: var(--text-muted);
  max-width: 900px;
}

.offline-label {
  margin: 0 0 10px;
  color: #6d5b19;
  font-weight: 600;
  font-size: 14px;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 26px;
}

.section-heading h2 {
  margin: 0;
  font-size: 32px;
  font-weight: 500;
}

.heart {
  color: #ff6c7d;
  font-size: 24px;
}

.factors-list {
  display: grid;
  gap: 24px;
  margin-bottom: 56px;
}

.factor-card {
  background: white;
  border-radius: 28px;
  box-shadow: var(--shadow-soft);
  padding: 40px;
}

.factor-card.mint {
  border: 1px solid rgba(55, 214, 176, 0.28);
}

.factor-left {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}

.factor-icon {
  width: 64px;
  height: 64px;
  min-width: 64px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  font-size: 28px;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.factor-icon.amber {
  background: #f4e4b9;
  color: #c96a14;
}

.factor-icon.pink {
  background: #f6dde3;
  color: #ef2f73;
}

.factor-icon.mint {
  background: #d8f4e9;
  color: #138067;
}

.factor-content {
  flex: 1;
  min-width: 0;
}

.factor-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.factor-top h3 {
  margin: 0;
  font-size: 28px;
  font-weight: 500;
}

.factor-badge {
  border-radius: 999px;
  padding: 12px 22px;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.factor-badge.amber {
  background: #fbf2dd;
  color: #cf7016;
  border: 1px solid #edd18e;
}

.factor-badge.pink {
  background: #fde7ee;
  color: #eb2c73;
  border: 1px solid #f5c7d5;
}

.factor-badge.mint {
  background: #e4f7ef;
  color: #138067;
  border: 1px solid #b7ead6;
}

.factor-description {
  margin: 0 0 14px;
  font-size: 18px;
  color: #485465;
}

.factor-note {
  margin: 0 0 20px;
  font-size: 17px;
  color: #7b8494;
  font-style: italic;
}

.factor-toggle {
  border: none;
  background: transparent;
  padding: 0;
  color: #00958f;
  font-size: 17px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.arrow {
  transition: transform 0.2s ease;
}

.arrow.open {
  transform: rotate(180deg);
}

.factor-extra {
  margin-top: 16px;
  color: var(--text-muted);
  line-height: 1.7;
  max-width: 900px;
}

.action-banner {
  position: relative;
  min-height: 360px;
  border-radius: 30px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.action-banner-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.action-banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8, 150, 123, 0.88),
    rgba(8, 150, 123, 0.72)
  );
}

.action-banner-content {
  position: relative;
  z-index: 2;
  color: white;
  max-width: 720px;
  padding: 56px 48px;
}

.action-banner-content h2 {
  margin: 0 0 18px;
  font-size: 36px;
  font-weight: 500;
}

.action-banner-content p {
  margin: 0 0 34px;
  font-size: 18px;
  line-height: 1.7;
}

.action-link {
  display: inline-flex;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 992px) {
  .hero-copy h1 {
    font-size: 54px;
  }

  .summary-card,
  .factor-card {
    padding: 28px;
  }

  .summary-text h2 {
    font-size: 30px;
  }
}

@media (max-width: 768px) {
  .insights-hero {
    padding: 40px 0 56px;
  }

  .brand-left {
    flex-wrap: wrap;
  }

  .hero-copy h1 {
    font-size: 40px;
    max-width: 100%;
  }

  .hero-copy p {
    font-size: 18px;
  }

  .summary-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
    margin-bottom: 48px;
  }

  .summary-icon {
    width: 82px;
    height: 82px;
    min-width: 82px;
    font-size: 34px;
  }

  .summary-text h2 {
    font-size: 28px;
  }

  .section-heading h2 {
    font-size: 24px;
  }

  .factor-left {
    flex-direction: column;
    gap: 20px;
  }

  .factor-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .factor-top h3 {
    font-size: 24px;
  }

  .action-banner-content {
    padding: 34px 24px;
  }

  .action-banner-content h2 {
    font-size: 28px;
  }

  .action-banner-content p {
    font-size: 16px;
  }
}
</style>
