<template>
  <div class="home-page">
    <div class="home-scroll-progress" :style="{ transform: `scaleX(${scrollProgress})` }" aria-hidden="true"></div>

    <!-- ════════════════════════════════════════
         1. HERO
    ════════════════════════════════════════ -->
    <section class="hero-section">
      <div class="container hero-grid">

        <div class="hero-copy">
          <div class="hero-badge reveal">
            <span class="hero-badge-dot"></span>
            Melbourne Air • Live Now
          </div>

          <h1 class="hero-heading reveal reveal-delay-1">
            They deserve to
            <em class="hero-heading-italic">breathe easy.</em>
          </h1>

          <p class="hero-subtext reveal reveal-delay-2">
          Every parent in Melbourne worries about their child breathing. We put that worry into something useful.
          </p>
          <p class="hero-subtext reveal reveal-delay-2" style="color:#8FE0DA;">
          Clear, real-time guidance, so you can make confident decisions for your family, every day.         
          </p>

          <div class="hero-actions reveal reveal-delay-3">
            <button type="button" class="btn-hero-primary" @click="scrollToAirSection">
              Check Air Quality Now
            </button>
            <router-link to="/asthma-learn" class="btn-hero-ghost">
              Learn More →
            </router-link>
          </div>
        </div>

        <div class="hero-image-wrap reveal reveal-delay-2">
          <img
            src="../assets/images/hero-family.jpg"
            alt="Parent and child outdoors"
            class="hero-image"
          />
          <div class="hero-image-badge">
            <span class="image-badge-dot"></span>
            Low Risk Today · Melbourne
          </div>        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════
         2. STATS
    ════════════════════════════════════════ -->
    <section ref="statsSection" class="stats-section">
      <div class="container stats-row">
        <div
          v-for="(stat, i) in stats"
          :key="stat.value"
          class="stat-item reveal"
          :class="`reveal-delay-${i + 1}`"
        >
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
          <span class="stat-desc">{{ stat.description }}</span>
        </div>
      </div>
    </section>

    <BestTimeCard
      :factors="displayFactors"
      :best-time-data="bestTimeData"
      :loading="bestTimeLoading"
      :error="bestTimeError"
      suburb="Melbourne"
      :hours="12"
      :auto-fetch="false"
    />

    <!-- ════════════════════════════════════════
         3. LIVE AIR INSIGHTS — FROM INSIGHTS API
    ════════════════════════════════════════ -->
    <section id="air-now" class="home-air-section">
      <div class="home-air-image-side reveal">
        <img
          src="../assets/images/melbourne-skyline-bg.jpg"
          alt="Melbourne park and skyline"
          class="home-air-image"
        />
      </div>

      <div class="home-air-content-side">
        <p class="home-air-kicker reveal">* MELBOURNE AIR TELLS A STORY EVERY DAY</p>
        <h2 class="home-air-heading reveal reveal-delay-1">
          What's in the air
          <br />right now
        </h2>
        <p class="home-air-copy reveal reveal-delay-2">
          Melbourne's air changes every hour, shaped by traffic, construction, pollen
          seasons, and weather. These four numbers tell you everything you need to know
          about what your child is breathing right now.
        </p>

        <p v-if="isOffline && usingCachedInsights" class="home-air-offline">
          You're offline — showing the latest saved insight.
        </p>

        <div class="home-air-list" aria-label="Live air quality factors">
          <article
            v-for="(factor, index) in homeAirFactors"
            :key="factor.title || factor.name || factor.label || index"
            class="home-air-factor"
            :class="`reveal-delay-${Math.min(index + 2, 4)}`"
          >
            <div class="home-air-factor-main">
              <span class="home-air-dot"></span>
              <div class="home-air-factor-text">
                <div class="home-air-title-row">
                  <h3>{{ factor.shortTitle || factor.title || factor.name || factor.label }}</h3>
                  <span
                    class="home-air-info-wrap"
                    tabindex="0"
                    :aria-label="`What does ${factor.shortTitle || factor.title || factor.name || factor.label} mean?`"
                  >
                    <span class="home-air-info">i</span>
                    <span class="home-air-tooltip" role="tooltip">
                      {{ pollutantTip(factor) }}
                    </span>
                  </span>
                </div>
                <p>{{ homeAirShortDescription(factor) }}</p>
              </div>
            </div>

            <div class="home-air-factor-value">
              <strong>{{ splitFactorValue(factor.value).number }}</strong>
              <span>{{ splitFactorValue(factor.value).unit }}</span>
            </div>

            <span class="home-air-status" :class="statusClass(factor.status)">
              {{ factor.status }}
            </span>
          </article>
        </div>

        <p class="home-air-source">EPA Victoria · Updated every hour</p>
      </div>
    </section>

    
    
    <!-- ════════════════════════════════════════
         4. DECISION TOOLS — IN ONE PLACE
    ════════════════════════════════════════ -->
    <section class="quick-section section">
      <div class="container quick-inner">

        <div class="quick-header reveal">
          <h2 class="quick-heading">Everything a Melbourne parent<br />needs, in one place.</h2>
          <p class="quick-sub">
            From the air outside to the products in your shopping trolley — BRTHEZ
            helps you make faster, calmer, more confident decisions for your child.
          </p>
        </div>

        <div class="quick-grid">
          <router-link
            v-for="(card, i) in quickCards"
            :key="card.title"
            :to="card.to"
            class="quick-card reveal"
            :class="[`reveal-delay-${i + 1}`, card.theme]"
          >
            <img
              v-if="card.image"
              :src="card.image"
              :alt="card.title"
              class="quick-card-image"
            />
            <div class="quick-card-overlay"></div>
            <div class="quick-card-body">
              <div class="quick-card-title-row">
                <h3 class="quick-card-title">{{ card.title }}</h3>
              </div>
              <p class="quick-card-desc">{{ card.description }}</p>
              <span class="quick-card-link">{{ card.linkText }} →</span>
            </div>
          </router-link>
        </div>

      </div>
    </section>

    <!-- ════════════════════════════════════════
         5. BECAUSE EVERY BREATH MATTERS
    ════════════════════════════════════════ -->
    <section class="closing-section">
      <img
        src="../assets/images/home-cta-bg.jpg"
        alt=""
        class="closing-bg-image"
        aria-hidden="true"
      />
      <div class="closing-bg-overlay" aria-hidden="true"></div>

      <div class="container closing-inner">
        <h2 class="closing-heading reveal">Because every breath matters</h2>
        <p class="closing-subtext reveal reveal-delay-1">
          We bring Melbourne's environmental data into one place and turn it into
          practical guidance you can trust. No medical jargon. No endless charts.
          Just answers — built for parents, by parents.
        </p>

        <div class="closing-icons">
          <div
            v-for="(item, i) in closingIcons"
            :key="item.label"
            class="closing-icon-item reveal"
            :class="`reveal-delay-${i + 1}`"
          >
            <div class="closing-icon-circle">{{ item.icon }}</div>
            <span class="closing-icon-label">{{ item.label }}</span>
            <span class="closing-icon-note">{{ item.note }}</span>
          </div>
        </div>

        <button type="button" class="btn-closing reveal reveal-delay-3" @click="openHowItWorksModal">
          Learn how BRTHEZ helps
        </button>
      </div>
    </section>

    <Teleport to="body">
      <div
        v-if="showHowItWorksModal"
        class="how-modal-backdrop"
        role="presentation"
        @click.self="closeHowItWorksModal"
      >
        <section
          class="how-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="how-modal-title"
        >
          <button
            type="button"
            class="how-modal-close"
            aria-label="Close how BRTHEZ works popup"
            @click="closeHowItWorksModal"
          >
            ×
          </button>

          <p class="how-modal-kicker">HOW BRTHEZ WORKS</p>
          <h2 id="how-modal-title" class="how-modal-title">
            We turn <em>complex data</em> into simple guidance
          </h2>
          <p class="how-modal-copy">
            Melbourne's environmental data is scattered across government databases,
            research institutions, and monitoring stations. Most parents have neither
            the time nor the tools to make sense of it. BRTHEZ does that work for you —
            automatically, every hour, in plain language.
          </p>

          <div class="how-modal-sources">
            <article v-for="source in howItWorksSources" :key="source.letter" class="how-source-card">
              <span class="how-source-letter">{{ source.letter }}</span>
              <div>
                <p class="how-source-label">Data source</p>
                <h3>{{ source.title }}</h3>
                <p>{{ source.output }}</p>
              </div>
            </article>
          </div>

          <p class="how-modal-note">
            No scientific background needed. No endless charts. BRTHEZ translates all of
            this into one clear answer — and tells you exactly what to do about it.
          </p>
        </section>
      </div>
    </Teleport>


    <!-- ════════════════════════════════════════
         6. COMPLEX DATA → SIMPLE GUIDANCE
    ════════════════════════════════════════ -->
    <section class="guidance-section section">
      <div class="container guidance-grid">

        <div class="guidance-copy">
          <p class="eyebrow reveal">Your peace of mind</p>
          <h2 class="guidance-heading reveal reveal-delay-1">
            We turn <em class="guidance-em">complex data</em> into simple
            guidance
          </h2>
          <p class="guidance-text reveal reveal-delay-2">
            BRTHEZ pulls from EPA Victoria, local government construction
            permits, and environmental monitoring stations to give you one clear
            answer: is today a good day for outdoor activities?
          </p>
          <p class="guidance-text reveal reveal-delay-2">
            No scientific background needed. No endless charts. Just practical,
            parent-friendly guidance you can trust.
          </p>
          <div class="guidance-actions reveal reveal-delay-3">
            <router-link to="/construction-dust" class="btn-pill btn-primary">
              Keep Them Safe
            </router-link>
          </div>
        </div>

        <div class="guidance-image-wrap reveal reveal-delay-2">
          <img
            src="../assets/images/complex-data-image.jpg"
            alt="Parent with child outdoors"
            class="guidance-image"
          />
          <div class="guidance-float-badge">
            <span class="float-check">✓</span>
            <span class="float-risk-dot"></span>
            <div>
              <p class="float-risk-label">Low Risk</p>
              <p class="float-risk-desc">Safe for outdoor play today</p>
            </div>
          </div>
        </div>

      </div>
    </section>

    

  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import BestTimeCard from '@/components/BestTimeCard.vue'

/* ── Page motion ───────────────────────────── */
const scrollProgress = ref(0)
const statsSection = ref(null)
const showHowItWorksModal = ref(false)

const updateScrollProgress = () => {
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  scrollProgress.value = maxScroll > 0 ? Math.min(scrollTop / maxScroll, 1) : 0
}

const scrollToStats = () => {
  statsSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const scrollToAirSection = () => {
  const airSection = document.getElementById('air-now')
  if (airSection) {
    airSection.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
  }
}

const openHowItWorksModal = () => {
  showHowItWorksModal.value = true
  document.body.classList.add('modal-open')
}

const closeHowItWorksModal = () => {
  showHowItWorksModal.value = false
  document.body.classList.remove('modal-open')
}

/* ── Data ─────────────────────────────────── */

const stats = [
  { value: '386K', label: 'Victorian children', description: 'living with asthma' },
  { value: '42%', label: 'of trigger events', description: 'linked to air quality' },
  { value: '26.5K', label: 'hospital visits', description: 'in Melbourne each year' },
  { value: '2 in 3', label: 'parents', description: 'concerned about outdoor air' },
]


const INSIGHTS_CACHE_KEY = 'safair_insights_cache_v1'

const factors = ref([])
const summaryTitle = ref('')
const summaryText = ref('')
const isOffline = ref(false)
const usingCachedInsights = ref(false)

const displayFactors = computed(() =>
  factors.value.map((factor) => ({
    ...factor,
    status: factor.status || factor.condition || factor.level || descriptionStatus(factor.description),
    description: factor.description || '',
    note: factor.note || '',
  }))
)

const homeAirFactors = computed(() =>
  displayFactors.value.slice(0, 4).map((factor) => ({
    ...factor,
    shortTitle: shortFactorTitle(factor.title || factor.name || factor.label),
  }))
)

const pollutantTips = {
  pm25:
    'Tiny invisible particles, smaller than a grain of sand. When these are high, they can slip deep into little lungs and make breathing harder. Think of them like invisible dust that triggers coughing fits.',
  pm10:
    'Bigger bits of dust, pollen, and mould floating in the air. You can sometimes spot these in a ray of sunlight. On windy Melbourne days these spike fast, worth checking before a park trip.',
  o3:
    "Ozone builds up on hot sunny afternoons, especially near busy roads. It's not the good ozone from up high, at ground level it stings airways. Highest risk between 2pm and 6pm on warm days.",
  no2:
    'This comes almost entirely from car exhausts. Highest during school drop-off and pick-up times near main roads. On high days, a quieter back street makes a real difference.',
}

function factorTipKey(title = '') {
  const lower = String(title).toLowerCase()
  if (lower.includes('pm2.5') || lower.includes('pm25')) return 'pm25'
  if (lower.includes('pm10')) return 'pm10'
  if (lower.includes('ozone') || lower.includes('o3')) return 'o3'
  if (lower.includes('no2') || lower.includes('nitrogen')) return 'no2'
  return ''
}

function pollutantTip(factor = {}) {
  const title = factor.shortTitle || factor.title || factor.name || factor.label || ''
  return pollutantTips[factorTipKey(title)] || factor.explanation || factor.description || factor.note || ''
}

function homeAirShortDescription(factor = {}) {
  return factor.description || factor.note || ''
}

function shortFactorTitle(title = '') {
  const lower = String(title).toLowerCase()
  if (lower.includes('pm2.5') || lower.includes('pm25')) return 'PM2.5'
  if (lower.includes('pm10')) return 'PM10'
  if (lower.includes('ozone') || lower.includes('o3')) return 'Ozone (O₃)'
  if (lower.includes('no2') || lower.includes('nitrogen')) return 'NO₂'
  return title
}

function descriptionStatus(description = '') {
  const lower = String(description).toLowerCase()
  if (lower.includes('very high')) return 'Very High'
  if (lower.includes('high')) return 'High'
  if (lower.includes('moderate')) return 'Moderate'
  if (lower.includes('good')) return 'Good'
  if (lower.includes('low')) return 'Low'
  return ''
}

function splitFactorValue(value = '') {
  const raw = String(value).trim()
  const match = raw.match(/^(-?\d+(?:\.\d+)?)(.*)$/)
  return {
    number: match ? match[1] : raw || '--',
    unit: match && match[2].trim() ? match[2].trim() : '',
  }
}

function statusClass(status = '') {
  const lower = String(status).toLowerCase()
  if (lower.includes('very')) return 'veryhigh'
  if (lower.includes('high')) return 'high'
  if (lower.includes('moderate')) return 'moderate'
  if (lower.includes('low')) return 'low'
  if (lower.includes('good')) return 'good'
  return ''
}

const buildInsightsUrl = () => {
  const baseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    'https://d204zergykc1k6.cloudfront.net'
  return `${baseUrl.replace(/\/$/, '')}/v1/insights?location=melbourne`
}

const normalizeInsightsPayload = (payload = {}) => ({
  summaryTitle: payload.summaryTitle || '',
  summaryText: payload.summaryText || '',
  factors: Array.isArray(payload.factors) ? payload.factors : [],
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
    console.error('Failed to load home insights', error)
  }
}


const bestTimeData = ref(null)
const bestTimeLoading = ref(false)
const bestTimeError = ref(null)

const buildBestTimeUrl = () => {
  const baseUrl = (
    import.meta.env.VITE_ASTHMASAFE_API_BASE ||
    import.meta.env.VITE_API_BASE ||
    'https://asthmasafe-api.onrender.com'
  ).replace(/\/$/, '')

  return `${baseUrl}/api/best-time?suburb=Melbourne&hours=12`
}

const loadBestTime = async () => {
  bestTimeLoading.value = true
  bestTimeError.value = null

  try {
    const response = await fetch(buildBestTimeUrl())
    const payload = await response.json()

    if (!response.ok || !payload.success) {
      throw new Error(payload.error || `Best-time API failed: ${response.status}`)
    }

    bestTimeData.value = payload
  } catch (error) {
    bestTimeError.value = error.message || 'Failed to load best-time forecast'
    console.error('Failed to load home best-time forecast', error)
  } finally {
    bestTimeLoading.value = false
  }
}

const quickCards = [
  {
    title: 'SafeShelf',
    description:
      "Before you put it in your trolley or under your sink, scan any product to check if its ingredients could trigger your child's asthma. From cleaning sprays to air fresheners, SafeShelf keeps your home safe.",
    image: new URL('../assets/images/home-safeshelf-bg.png', import.meta.url).href,
    to: '/housing-scanner',
    linkText: 'Open SafeShelf',
    theme: 'quick-card-teal',
  },
  {
    title: 'ClearPath',
    description:
      'Find the cleanest path to your destination, avoiding construction zones, high-traffic roads, and pollen hotspots before you leave home.',
    image: new URL('../assets/images/route-planning.jpg', import.meta.url).href,
    to: '/construction-dust',
    linkText: 'Find a ClearPath',
    theme: 'quick-card-blue',
  },
  {
    title: 'DustWatch',
    description:
      "See which construction sites near your suburb are active today and how much dust they're generating, so you know what's in the air before you head out with your child.",
    image: new URL('../assets/images/home-construction-bg.png', import.meta.url).href,
    to: '/construction-dust',
    linkText: 'Open DustWatch',
    theme: 'quick-card-earth',
  },
  {
    title: 'SafeSpots',
    description:
      'Discover child-friendly parks and outdoor spaces across Melbourne rated for asthma safety, so you can plan a great day out, confidently.',
    image: new URL('../assets/images/home-safespots-bg.png', import.meta.url).href,
    to: '/construction-dust',
    linkText: 'Find a SafeSpot',
    theme: 'quick-card-green',
  },
]


const closingIcons = [
  { icon: '⌁', label: 'Live air data', note: 'Real-time from EPA Victoria' },
  { icon: '⌖', label: 'Local insights', note: 'Tailored to your suburb' },
  { icon: '♡', label: 'Parent-focused', note: 'No medical degree required' },
]

const howItWorksSources = [
  {
    letter: 'A',
    title: 'EPA Victoria + Bureau of Meteorology',
    output: 'Air quality risk rating and best time to go outside',
  },
  {
    letter: 'B',
    title: 'City of Melbourne construction permits',
    output: 'Live dust risk map and suburb-level alerts',
  },
  {
    letter: 'C',
    title: 'Open pollen and allergen datasets',
    output: 'Route safety scores and hotspot warnings',
  },
  {
    letter: 'D',
    title: 'Global respiratory chemical databases',
    output: 'SafeShelf ingredient risk classification',
  },
]

/* ── Scroll reveal ────────────────────────── */
let observer = null

onMounted(() => {
  loadInsights()
  loadBestTime()

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  )

  updateScrollProgress()
  window.addEventListener('scroll', updateScrollProgress, { passive: true })

  // Trigger hero elements immediately (they're already in view)
  document.querySelectorAll('.hero-section .reveal').forEach((el) => {
    setTimeout(() => el.classList.add('visible'), 80)
  })

  // Observe everything else
  document.querySelectorAll('.home-page .reveal:not(.hero-section .reveal)').forEach((el) => {
    observer.observe(el)
  })
})

onBeforeUnmount(() => {
  if (observer) observer.disconnect()
  window.removeEventListener('scroll', updateScrollProgress)
  document.body.classList.remove('modal-open')
})
</script>

<style scoped>
/* ════════════════════════════════════════
   PAGE BASE
════════════════════════════════════════ */
.home-page {
  background: var(--bg-page);
  min-height: 100vh;
  overflow-x: hidden;
}

.home-scroll-progress {
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

/* ════════════════════════════════════════
   1. HERO
════════════════════════════════════════ */
.hero-section {
  position: relative;
  overflow: hidden;
  background: linear-gradient(
    155deg,
    #3bbfaa 0%,
    #1a8a78 22%,
    #0d6055 55%,
    #073d34 100%
  );
  padding: 88px 0 100px;
}

.hero-grid {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  background: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.92);
  border-radius: 999px;
  padding: 9px 18px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 26px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(6px);
  width: fit-content;
}

.hero-badge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #5ef0d0;
  box-shadow: 0 0 8px #5ef0d0;
  animation: pulse-dot 2.4s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.6; transform: scale(0.8); }
}

.hero-heading {
  margin: 0 0 22px;
  font-family: var(--font-serif);
  font-size: 66px;
  font-weight: 500;
  line-height: 1.05;
  color: white;
}

.hero-heading-italic {
  display: block;
  font-style: italic;
  font-weight: 400;
  color: #8FE0DA;
}

.hero-subtext {
  margin: 0 0 36px;
  font-size: 17px;
  line-height: 1.78;
  color: rgba(255, 255, 255, 0.78);
  max-width: 460px;
  font-weight: bold;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.btn-hero-primary {
  display: inline-flex;
  align-items: center;
  background: white;
  color: var(--primary-dark);
  border-radius: 999px;
  padding: 16px 30px;
  font-size: 15px;
  font-weight: 700;
  transition: transform 0.22s var(--ease-out-quart), box-shadow 0.22s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.18);
}

.btn-hero-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.26);
}

.btn-hero-ghost {
  color: rgba(255, 255, 255, 0.82);
  font-size: 15px;
  font-weight: 600;
  transition: color 0.18s ease, letter-spacing 0.18s ease;
}

.btn-hero-ghost:hover {
  color: white;
  letter-spacing: 0.01em;
}

.hero-image-wrap {
  position: relative;
  position: relative;
}

.hero-image {
  width: 100%;
  height: 450px;
  object-fit: cover;
  border-radius: 22px;
  box-shadow: 0 28px 60px rgba(0, 0, 0, 0.28);
  transition: transform 0.5s var(--ease-out-expo);
}

.hero-image-wrap:hover .hero-image {
  transform: scale(1.015);
}

.hero-image-badge {
  position: absolute;
  bottom: 22px;
  left: 22px;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  background: rgba(4, 18, 14, 0.75);
  color: white;
  border-radius: 999px;
  padding: 11px 20px;
  font-size: 14px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.image-badge-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #5ef0d0;
}

/* ════════════════════════════════════════
   2. STATS
════════════════════════════════════════ */
.stats-section {
  background: #fbfaf7;
  padding: 68px 0 74px;
  border-bottom: 1px solid rgba(15, 45, 40, 0.06);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  align-items: center;
}

.stat-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
  min-height: 112px;
  justify-content: center;
  padding: 0 34px;
}

.stat-item:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 14px;
  right: 0;
  width: 1px;
  height: 76px;
  background: rgba(120, 89, 60, 0.18);
}

.stat-value {
  font-family: var(--font-serif);
  font-size: clamp(42px, 4vw, 56px);
  font-weight: 600;
  color: var(--primary);
  line-height: 0.95;
  letter-spacing: 0.01em;
}

.stat-label {
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0;
  text-transform: none;
  color: var(--text-dark);
  line-height: 1.2;
}

.stat-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.35;
}

/* ════════════════════════════════════════
   3. LIVE AIR INSIGHTS — HOME
════════════════════════════════════════ */
.home-air-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 620px;
  background: var(--bg-cream, #faf7f2);
}

.home-air-image-side {
  overflow: hidden;
  background: #f8f5ef;
}

.home-air-image {
  width: 100%;
  height: 100%;
  min-height: 620px;
  display: block;
  object-fit: cover;
  transition: transform 0.7s var(--ease-out-expo);
}

.home-air-image-side:hover .home-air-image {
  transform: scale(1.025);
}

.home-air-content-side {
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #0b675c;
  color: white;
  padding: 72px min(7vw, 76px);
}

.home-air-kicker {
  margin: 0 0 20px;
  color: rgba(166, 224, 214, 0.9);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.home-air-heading {
  margin: 0 0 22px;
  max-width: 460px;
  color: white;
  font-family: var(--font-serif);
  font-size: clamp(40px, 4.7vw, 58px);
  font-weight: 600;
  line-height: 1.08;
  letter-spacing: -0.025em;
}

.home-air-copy {
  margin: 0 0 34px;
  max-width: 660px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 17px;
  line-height: 1.7;
}

.home-air-offline {
  margin: -18px 0 20px;
  color: #f1c47a;
  font-size: 13px;
  font-weight: 700;
}

.home-air-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.home-air-factor {
  position: relative;
  display: grid;
  grid-template-columns: minmax(170px, 1fr) auto auto;
  align-items: center;
  gap: 18px;
  min-height: 74px;
  padding: 15px 20px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.145);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(6px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
  transition: transform 0.22s var(--ease-out-quart), background 0.22s ease, border-color 0.22s ease;
  opacity: 1;
  transform: none;
}

.home-air-factor:hover {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.19);
  border-color: rgba(159, 230, 219, 0.24);
}

.home-air-factor-main {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.home-air-factor-text {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 6px;
}

.home-air-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.home-air-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #9fe6db;
  flex-shrink: 0;
}

.home-air-factor h3 {
  margin: 0;
  color: white;
  font-size: 15px;
  font-weight: 800;
}

.home-air-info-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  outline: none;
}

.home-air-info {
  display: inline-grid;
  place-items: center;
  width: 16px;
  height: 16px;
  border: 1px solid rgba(159, 230, 219, 0.75);
  border-radius: 50%;
  color: rgba(159, 230, 219, 0.9);
  font-size: 10px;
  font-weight: 800;
  font-style: italic;
  line-height: 1;
  cursor: help;
  transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
}

.home-air-info-wrap:hover .home-air-info,
.home-air-info-wrap:focus-visible .home-air-info {
  background: #9fe6db;
  color: #073d34;
  border-color: #9fe6db;
}

.home-air-tooltip {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 14px);
  z-index: 20;
  width: min(330px, 70vw);
  padding: 16px 18px;
  border-radius: 16px;
  background: rgba(8, 25, 22, 0.96);
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 500;
  line-height: 1.62;
  letter-spacing: 0;
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
  transform: translate(-50%, 8px);
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity 0.18s ease, transform 0.18s ease, visibility 0.18s ease;
}

.home-air-tooltip::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -7px;
  width: 14px;
  height: 14px;
  background: rgba(8, 25, 22, 0.96);
  transform: translateX(-50%) rotate(45deg);
}

.home-air-info-wrap:hover .home-air-tooltip,
.home-air-info-wrap:focus-visible .home-air-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, 0);
}

.home-air-factor-value {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  gap: 5px;
  color: white;
  white-space: nowrap;
}

.home-air-factor-value strong {
  font-family: var(--font-serif);
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.home-air-factor-value span {
  color: rgba(255, 255, 255, 0.78);
  font-size: 12px;
  font-weight: 700;
}

.home-air-status {
  justify-self: start;
  border-radius: 999px;
  padding: 6px 12px;
  background: rgba(20, 151, 137, 0.85);
  color: white;
  font-size: 12px;
  font-weight: 800;
  line-height: 1;
}

.home-air-status.moderate { background: rgba(212, 132, 74, 0.92); }
.home-air-status.high,
.home-air-status.veryhigh { background: rgba(200, 64, 64, 0.92); }
.home-air-status.low { background: rgba(20, 151, 137, 0.85); }

.home-air-factor p {
  margin: 0;
  color: rgba(255, 255, 255, 0.64);
  font-size: 12px;
  line-height: 1.35;
}

.home-air-source {
  display: block;
  margin: 24px 0 0;
  color: rgba(255, 255, 255, 0.58);
  font-size: 13px;
  font-weight: 600;
}

/* ════════════════════════════════════════
   3. DECISION TOOLS
════════════════════════════════════════ */
.quick-section {
  background: #fbfaf7;
  padding-top: 92px;
}

.quick-inner {
  max-width: 1120px;
}

.quick-header {
  text-align: center;
  margin-bottom: 56px;
}

.quick-heading {
  font-family: var(--font-serif);
  font-size: clamp(38px, 4vw, 54px);
  font-weight: 600;
  color: var(--text-dark);
  margin: 0 0 18px;
  line-height: 1.16;
  letter-spacing: -0.02em;
}

.quick-sub {
  margin: 0 auto;
  max-width: 610px;
  font-size: 17px;
  color: var(--text-muted);
  line-height: 1.75;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
}

.quick-card {
  position: relative;
  min-height: 300px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  border-radius: 22px;
  text-decoration: none;
  color: white;
  background: #0d5c57;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 14px 42px rgba(9, 44, 38, 0.12);
  transition:
    transform 0.28s var(--ease-out-quart),
    box-shadow 0.28s ease;
}

.quick-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 24px 60px rgba(9, 44, 38, 0.2);
}

.quick-card-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.55s var(--ease-out-expo);
}

.quick-card:hover .quick-card-image {
  transform: scale(1.045);
}

.quick-card-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(105deg, rgba(3, 54, 47, 0.9) 0%, rgba(3, 54, 47, 0.76) 48%, rgba(3, 54, 47, 0.38) 100%),
    linear-gradient(to top, rgba(0, 0, 0, 0.5), transparent 62%);
}

.quick-card-blue .quick-card-overlay {
  background:
    linear-gradient(105deg, rgba(19, 38, 85, 0.92) 0%, rgba(19, 38, 85, 0.78) 52%, rgba(19, 38, 85, 0.35) 100%),
    linear-gradient(to top, rgba(0, 0, 0, 0.45), transparent 62%);
}

.quick-card-earth .quick-card-overlay {
  background:
    linear-gradient(105deg, rgba(92, 48, 17, 0.9) 0%, rgba(92, 48, 17, 0.73) 52%, rgba(92, 48, 17, 0.32) 100%),
    linear-gradient(to top, rgba(0, 0, 0, 0.46), transparent 62%);
}

.quick-card-green .quick-card-overlay {
  background:
    linear-gradient(105deg, rgba(26, 74, 42, 0.9) 0%, rgba(26, 74, 42, 0.75) 52%, rgba(26, 74, 42, 0.32) 100%),
    linear-gradient(to top, rgba(0, 0, 0, 0.42), transparent 62%);
}

.quick-card-body {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 34px 34px 32px;
}

.quick-card-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.quick-card-title {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 30px;
  font-weight: 700;
  color: white;
  line-height: 1.1;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.22);
}

.quick-card-desc {
  max-width: 570px;
  margin: 0 0 22px;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.88);
}

.quick-card-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  border-radius: 999px;
  padding: 0 22px;
  background: white;
  color: #123b35;
  font-size: 14px;
  font-weight: 700;
  transition: transform 0.2s var(--ease-out-quart), box-shadow 0.2s ease;
}

.quick-card:hover .quick-card-link {
  transform: translateX(3px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
}



/* ════════════════════════════════════════
   6. GUIDANCE — COMPLEX DATA
════════════════════════════════════════ */
.guidance-section {
  background: var(--bg-white);
}

.guidance-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 72px;
  align-items: center;
}

.guidance-heading {
  font-family: var(--font-serif);
  font-size: 40px;
  font-weight: 500;
  line-height: 1.2;
  color: var(--text-dark);
  margin: 0 0 22px;
}

.guidance-em {
  font-style: italic;
  color: var(--primary);
}

.guidance-text {
  margin: 0 0 16px;
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-body);
}

.guidance-actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 30px;
}

.guidance-image-wrap {
  position: relative;
}

.guidance-image {
  width: 100%;
  height: 480px;
  object-fit: cover;
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
  transition: transform 0.5s var(--ease-out-expo);
}

.guidance-image-wrap:hover .guidance-image {
  transform: scale(1.015);
}

.guidance-float-badge {
  position: absolute;
  bottom: 26px;
  left: 26px;
  background: white;
  border-radius: 16px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.14);
  min-width: 210px;
  transition: transform 0.25s var(--ease-out-quart);
}

.guidance-image-wrap:hover .guidance-float-badge {
  transform: translateY(-3px);
}

.float-check {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--teal-light);
  color: var(--primary);
  font-size: 15px;
  font-weight: 700;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.float-risk-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
}

.float-risk-label {
  margin: 0 0 2px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-dark);
}

.float-risk-desc {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
}

/* ════════════════════════════════════════
   7. CLOSING — EVERY BREATH MATTERS
════════════════════════════════════════ */
.closing-section {
  position: relative;
  overflow: hidden;
  background: #178f80;
  padding: 104px 0 94px;
  isolation: isolate;
}

.closing-bg-image {
  position: absolute;
  inset: 0;
  z-index: -2;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.70;
  filter: saturate(0.9) contrast(0.95);
}

.closing-bg-overlay {
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(
    180deg,
    rgba(17, 144, 130, 0.88) 0%,
    rgba(9, 111, 100, 0.9) 100%
  );
}

.closing-inner {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.closing-heading {
  font-family: var(--font-serif);
  font-size: clamp(42px, 4.6vw, 58px);
  font-weight: 600;
  color: white;
  margin: 0 0 24px;
  line-height: 1.08;
  letter-spacing: -0.02em;
}

.closing-subtext {
  margin: 0 0 46px;
  font-size: 18px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.88);
  max-width: 730px;
}

.closing-icons {
  display: flex;
  gap: clamp(42px, 7vw, 92px);
  justify-content: center;
  margin-bottom: 48px;
  flex-wrap: wrap;
}

.closing-icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 150px;
}

.closing-icon-circle {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.22);
  display: grid;
  place-items: center;
  font-size: 26px;
  color: white;
  transition: background 0.22s ease, transform 0.22s var(--ease-out-quart);
}

.closing-icon-item:hover .closing-icon-circle {
  background: rgba(255, 255, 255, 0.28);
  transform: translateY(-3px);
}

.closing-icon-label {
  margin-top: 4px;
  font-size: 15px;
  font-weight: 800;
  color: white;
}

.closing-icon-note {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.78);
}

.btn-closing {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  background: white;
  color: var(--primary-dark);
  border-radius: 999px;
  padding: 18px 38px;
  font-size: 15px;
  font-weight: 800;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: transform 0.22s var(--ease-out-quart), box-shadow 0.22s ease;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
}

.btn-closing:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.24);
}

.how-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 999;
  display: grid;
  place-items: center;
  padding: 32px 18px;
  background: rgba(8, 24, 22, 0.58);
  backdrop-filter: blur(9px);
}

.how-modal {
  position: relative;
  width: min(620px, 100%);
  max-height: min(84vh, 760px);
  overflow-y: auto;
  border-radius: 24px;
  background: #fffdf9;
  padding: 42px 38px 38px;
  box-shadow: 0 34px 90px rgba(0, 0, 0, 0.32);
}

.how-modal-close {
  position: absolute;
  top: 28px;
  right: 28px;
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 50%;
  background: #e8f6f3;
  color: var(--primary);
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
}

.how-modal-kicker {
  margin: 0 0 26px;
  color: #1b9b91;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.how-modal-title {
  margin: 0 40px 16px 0;
  color: var(--text-dark);
  font-family: var(--font-serif);
  font-size: clamp(28px, 3vw, 34px);
  line-height: 1.15;
  font-weight: 700;
}

.how-modal-title em {
  color: var(--primary);
  font-style: italic;
}

.how-modal-copy {
  margin: 0 0 26px;
  color: var(--text-muted);
  font-size: 15px;
  line-height: 1.72;
}

.how-modal-sources {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.how-source-card {
  display: grid;
  grid-template-columns: 40px 1fr;
  gap: 16px;
  align-items: center;
  padding: 16px 18px;
  border: 1px solid rgba(128, 95, 58, 0.18);
  border-radius: 15px;
  background: #fffaf4;
}

.how-source-letter {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  font-size: 13px;
  font-weight: 800;
}

.how-source-label {
  margin: 0 0 4px;
  color: var(--text-muted);
  font-size: 11px;
}

.how-source-card h3 {
  margin: 0 0 6px;
  color: var(--text-dark);
  font-size: 13px;
  font-weight: 800;
}

.how-source-card p:last-child {
  margin: 0;
  color: var(--primary);
  font-size: 13px;
  font-weight: 700;
}

.how-source-card p:last-child::before {
  content: '— ';
}

.how-modal-note {
  margin: 18px 0 0;
  padding: 17px 18px;
  border-radius: 14px;
  background: #e8f6f3;
  color: #0b675c;
  font-size: 14px;
  line-height: 1.6;
}

:global(body.modal-open) {
  overflow: hidden;
}


/* ════════════════════════════════════════
   RESPONSIVE
════════════════════════════════════════ */
@media (max-width: 992px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .hero-heading { font-size: 52px; }

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    row-gap: 42px;
  }

  .stat-item:nth-child(2)::after { display: none; }

  .quick-grid { grid-template-columns: 1fr; }

  .guidance-grid { grid-template-columns: 1fr; gap: 40px; }

  .closing-heading { font-size: 40px; }
}

@media (max-width: 768px) {
  .hero-section { padding: 60px 0 72px; }
  .hero-heading { font-size: 40px; }
  .hero-image { height: 300px; }

  .stats-section { padding: 48px 0 54px; }
  .stats-row { grid-template-columns: 1fr; row-gap: 28px; }
  .stat-item { min-height: auto; padding: 0 18px 26px; }
  .stat-item::after {
    top: auto !important;
    right: 50% !important;
    bottom: 0;
    width: 80px !important;
    height: 1px !important;
    transform: translateX(50%);
  }
  .stat-item:last-child::after { display: none; }
  .stat-value { font-size: 44px; }

  .quick-heading { font-size: 32px; }


  .guidance-heading { font-size: 30px; }
  .guidance-image { height: 320px; }
  .guidance-float-badge { bottom: 14px; left: 14px; padding: 12px 14px; }

  .closing-heading { font-size: 34px; }
  .closing-icons { gap: 28px; }
  .closing-icon-circle { width: 62px; height: 62px; font-size: 24px; }
}

@media (max-width: 980px) {
  .home-air-section {
    grid-template-columns: 1fr;
  }

  .home-air-image {
    min-height: 340px;
  }

  .home-air-content-side {
    padding: 56px 28px;
  }

  .home-air-factor {
    grid-template-columns: 1fr auto;
  }

  .home-air-status {
    justify-self: end;
  }

  .home-air-factor p {
    grid-column: 1 / -1;
  }

  .home-air-tooltip {
    left: auto;
    right: -10px;
    transform: translate(0, 8px);
  }

  .home-air-tooltip::after {
    left: auto;
    right: 13px;
    transform: rotate(45deg);
  }

  .home-air-info-wrap:hover .home-air-tooltip,
  .home-air-info-wrap:focus-visible .home-air-tooltip {
    transform: translate(0, 0);
  }
}

@media (max-width: 640px) {
  .home-air-factor {
    grid-template-columns: 1fr;
    align-items: flex-start;
    gap: 10px;
  }

  .home-air-factor-value,
  .home-air-status {
    justify-self: start;
  }
}

</style>

<style scoped>


.hero-image-wrap {
  animation: heroImageFloat 6s ease-in-out infinite;
  will-change: transform;
}

@keyframes heroImageFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-12px) rotate(-0.35deg); }
}

@media (prefers-reduced-motion: reduce) {
  .hero-image-wrap { animation: none; }
}
@media (max-width: 980px) {
  .home-air-section {
    grid-template-columns: 1fr;
  }

  .home-air-image {
    min-height: 340px;
  }

  .home-air-content-side {
    padding: 56px 28px;
  }

  .home-air-factor {
    grid-template-columns: 1fr auto;
  }

  .home-air-status {
    justify-self: end;
  }

  .home-air-factor p {
    grid-column: 1 / -1;
  }
}

@media (max-width: 640px) {
  .home-air-factor {
    grid-template-columns: 1fr;
    align-items: flex-start;
    gap: 10px;
  }

  .home-air-factor-value,
  .home-air-status {
    justify-self: start;
  }
}

</style>
