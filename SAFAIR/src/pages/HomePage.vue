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
            Melbourne Air — Live Now
          </div>

          <h1 class="hero-heading reveal reveal-delay-1">
            They deserve to
            <em class="hero-heading-italic">breathe easy.</em>
          </h1>

          <p class="hero-subtext reveal reveal-delay-2">
            Real-time air quality insights for Melbourne families. Make informed
            decisions about outdoor activities.
          </p>

          <div class="hero-actions reveal reveal-delay-3">
            <router-link to="/insights" class="btn-hero-primary">
              Check Air Quality Now
            </router-link>
            <router-link to="/insights" class="btn-hero-ghost">
              Learn more →
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
         2. STATS — QUOTE + NUMBERS
    ════════════════════════════════════════ -->
    <section ref="statsSection" class="stats-section section">
      <div class="container stats-grid">

        <div class="stats-quote reveal">
          <blockquote>
            Every parent in Melbourne worries about their child breathing. We
            put that worry into something useful.
          </blockquote>
        </div>

        <div class="stats-numbers">
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

      </div>
    </section>

     <!-- ════════════════════════════════════════
         6. WHY IT MATTERS — SPLIT PANEL
    ════════════════════════════════════════ -->
    <section class="story-section">
      <div class="story-image-side">
        <img
          src="../assets/images/melbourne-skyline-bg.jpg"
          alt="Melbourne skyline at sunset"
          class="story-image"
        />
      </div>
      <div class="story-content-side">
        <p class="eyebrow eyebrow-light reveal">Why it matters</p>
        <h2 class="story-heading reveal reveal-delay-1">
          Melbourne air tells a story every day
        </h2>
        <div class="story-items">
          <div
            v-for="(item, i) in storyItems"
            :key="item.title"
            class="story-item reveal"
            :class="`reveal-delay-${i + 2}`"
          >
            <div class="story-item-icon">{{ item.icon }}</div>
            <div>
              <p class="story-item-title">{{ item.title }}</p>
              <p class="story-item-desc">{{ item.subtitle }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- ════════════════════════════════════════
         3. QUICK ACCESS — WHAT TO DO TODAY
    ════════════════════════════════════════ -->
    <section class="quick-section section">
      <div class="container">

        <div class="quick-header reveal">
          <h2 class="quick-heading">What would you like to do today?</h2>
          <p class="quick-sub">Quick access to the tools and information you need most</p>
        </div>

        <div class="quick-grid">
          <router-link
            v-for="(card, i) in quickCards"
            :key="card.title"
            :to="card.to"
            class="quick-card reveal"
            :class="`reveal-delay-${i + 1}`"
          >
            <div class="quick-card-icon-wrap">
              <span class="quick-card-icon">{{ card.icon }}</span>
            </div>
            <div class="quick-card-body">
              <h3 class="quick-card-title">{{ card.title }}</h3>
              <p class="quick-card-desc">{{ card.description }}</p>
              <span class="quick-card-link">{{ card.linkText }} →</span>
            </div>
          </router-link>
        </div>

      </div>
    </section>

    <!-- ════════════════════════════════════════
         4. MORE WAYS — FEATURE CARDS
    ════════════════════════════════════════ -->
    <section class="features-section section">
      <div class="container">
        <p class="eyebrow reveal">Newly Launched</p>
        <h2 class="section-title reveal reveal-delay-1">More ways to protect your family</h2>

        <div class="feature-cards-grid">
          <article
            v-for="(card, i) in featureCards"
            :key="card.title"
            class="feature-card reveal"
            :class="`reveal-delay-${i + 1}`"
          >
            <div class="feature-card-image-wrap">
              <img :src="card.image" :alt="card.title" class="feature-card-image" />
              <span class="feature-card-badge">NEW</span>
            </div>
            <div class="feature-card-body">
              <div class="feature-card-icon">{{ card.icon }}</div>
              <h3 class="feature-card-title">{{ card.title }}</h3>
              <p class="feature-card-desc">{{ card.description }}</p>
              <router-link :to="card.to" class="feature-card-link">
                {{ card.linkText }} →
              </router-link>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════
         5. ACTIVE ALERT
    ════════════════════════════════════════ -->
    <section class="alert-section">
      <div class="container">
        <div class="alert-card reveal">
          <div class="alert-icon-wrap">
            <div class="alert-icon">≋</div>
          </div>
          <div class="alert-body">
            <p class="alert-eyebrow">Active Alert</p>
            <h2 class="alert-heading">
              High dust activity in Southbank and South Melbourne
            </h2>
            <p class="alert-desc">
              12 active construction sites within 2km of your location are
              reporting elevated dust levels today.
            </p>
            <ul class="alert-list">
              <li>Avoid outdoor play between 10 AM and 3 PM</li>
              <li>Consider indoor activities or parks away from construction</li>
              <li>Keep rescue inhaler accessible if venturing outdoors</li>
            </ul>
            <router-link to="/construction-dust" class="alert-cta">
              View full dust report →
            </router-link>
          </div>
        </div>
      </div>
    </section>

   

    <!-- ════════════════════════════════════════
         7. COMPLEX DATA → SIMPLE GUIDANCE
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
            <router-link to="/recommendations" class="btn-pill btn-primary">
              See Today's Report
            </router-link>
            <router-link to="/insights" class="btn-pill btn-outline">
              How It Works
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

    <!-- ════════════════════════════════════════
         8. BECAUSE EVERY BREATH MATTERS
    ════════════════════════════════════════ -->
    <section class="closing-section">
      <div class="container closing-inner">
        <h2 class="closing-heading reveal">Because every breath matters</h2>
        <p class="closing-subtext reveal reveal-delay-1">
          We bring Melbourne's environmental data into one place and turn it
          into practical guidance you can trust. Built by parents, for parents.
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
          </div>
        </div>
        <router-link to="/insights" class="btn-closing reveal reveal-delay-3">
          Learn how BRTHEZ helps
        </router-link>
      </div>
    </section>

  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'

/* ── Page motion ───────────────────────────── */
const scrollProgress = ref(0)
const statsSection = ref(null)

const updateScrollProgress = () => {
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  scrollProgress.value = maxScroll > 0 ? Math.min(scrollTop / maxScroll, 1) : 0
}

const scrollToStats = () => {
  statsSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

/* ── Data ─────────────────────────────────── */

const stats = [
  { value: '386K',   label: 'Victorian Children', description: 'Living with asthma' },
  { value: '42%',   label: 'Trigger Events',      description: 'Linked to air quality' },
  { value: '26.5K', label: 'Hospital Visits',     description: 'Each year in Melbourne' },
  { value: '2 in 3', label: 'Parents Concerned',  description: 'About outdoor air' },
]


const quickCards = [
  {
    title: 'Understand the air',
    description: "See what's in the air right now and what it means for your family.",
    icon: '≋',
    to: '/insights',
    linkText: 'View insights',
  },
  {
    title: 'Get local assistance',
    description: 'Check construction dust, find safer routes, and scan household products.',
    icon: '⊕',
    to: '/construction-dust',
    linkText: 'Browse assistance',
  },
  {
    title: 'Find better times',
    description: 'Discover gentler windows for outdoor activity based on forecasts.',
    icon: '◔',
    to: '/insights',
    linkText: 'Check times',
  },
  {
    title: 'Learn and prepare',
    description: 'Understand triggers, symptoms, and how to stay prepared.',
    icon: '◫',
    to: '/recommendations',
    linkText: 'Start learning',
  },
]

const storyItems = [
  { icon: '▦', title: 'Construction Dust',   subtitle: 'Track nearby building sites' },
  { icon: '❋', title: 'Pollen & Pollutants', subtitle: 'Real-time monitoring data' },
  { icon: '◎', title: 'Indoor Triggers',     subtitle: 'Scan household products' },
]

const featureCards = [
  {
    title: 'Asthma-Safe Route Planning',
    description: 'Plan your walks, bike rides, and school drop-offs to avoid construction zones, high-traffic roads, and pollen hotspots.',
    icon: '🗺',
    image: new URL('../assets/images/route-planning.jpg', import.meta.url).href,
    to: '/insights',
    linkText: 'Try Route Planner',
  },
  {
    title: 'Housing Product Scanner',
    description: 'Scan ingredient labels and barcodes to check if cleaning products, air fresheners, and sprays contain asthma triggers.',
    icon: '🔍',
    image: new URL('../assets/images/because-family.jpeg', import.meta.url).href,
    to: '/recommendations',
    linkText: 'Open Scanner',
  },
]

const closingIcons = [
  { icon: '☁', label: 'Live air data' },
  { icon: '⊞', label: 'Local insights' },
  { icon: '♡', label: 'Parent-focused' },
]

/* ── Scroll reveal ────────────────────────── */
let observer = null

onMounted(() => {
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
  /* Lighter, softer gradient — clear teal → mid → deep but not jet black */
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
}

.hero-subtext {
  margin: 0 0 36px;
  font-size: 17px;
  line-height: 1.78;
  color: rgba(255, 255, 255, 0.78);
  max-width: 460px;
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


.hero-floating-art {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: grid;
  place-items: center;
}

.hero-art-emoji {
  position: relative;
  z-index: 2;
  font-size: 42px;
  filter: drop-shadow(0 16px 28px rgba(0, 0, 0, 0.22));
  animation: floatHeroIcon 4.8s ease-in-out infinite;
}

.hero-art-orb {
  position: absolute;
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(2px);
}

.hero-art-orb-one {
  width: 190px;
  height: 128px;
  transform: rotate(-9deg);
}

.hero-art-orb-two {
  width: 118px;
  height: 88px;
  right: 42px;
  bottom: 48px;
}

.home-scroll-cue {
  position: absolute;
  left: 50%;
  bottom: -42px;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border: 0;
  background: rgba(255, 255, 255, 0.14);
  color: rgba(255, 255, 255, 0.82);
  border-radius: 999px;
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transform: translateX(-50%);
  transition: transform 0.24s var(--ease-out-quart), background 0.24s ease;
}

.home-scroll-cue:hover {
  transform: translateX(-50%) translateY(3px);
  background: rgba(255, 255, 255, 0.22);
}

.home-scroll-line {
  width: 1px;
  height: 28px;
  background: rgba(255, 255, 255, 0.75);
  animation: homeScrollPulse 1.8s ease-in-out infinite;
}

@keyframes floatHeroIcon {
  0%, 100% { transform: translateY(0) rotate(-2deg); }
  50% { transform: translateY(-13px) rotate(2deg); }
}

@keyframes homeScrollPulse {
  0%, 100% { transform: scaleY(0.45); opacity: 0.45; }
  50% { transform: scaleY(1); opacity: 1; }
}

/* ════════════════════════════════════════
   2. STATS — QUOTE + NUMBERS
════════════════════════════════════════ */
.stats-section {
  background: var(--bg-white);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 80px;
  align-items: center;
}

.stats-quote {
  border-left: 4px solid var(--primary);
  padding-left: 32px;
}

.stats-quote blockquote {
  margin: 0;
  font-family: var(--font-serif);
  font-style: italic;
  font-size: 26px;
  line-height: 1.6;
  color: var(--primary-dark);
  font-weight: 400;
}

.stats-numbers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 36px 44px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-family: var(--font-serif);
  font-size: 38px;
  font-weight: 500;
  color: var(--primary);
  line-height: 1;
}

.stat-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dark);
  margin-top: 6px;
}

.stat-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.45;
}

/* ════════════════════════════════════════
   3. QUICK ACCESS
════════════════════════════════════════ */
.quick-section {
  background: var(--bg-page);
}

.quick-header {
  text-align: center;
  margin-bottom: 48px;
}

.quick-heading {
  font-family: var(--font-serif);
  font-size: 42px;
  font-weight: 500;
  color: var(--text-dark);
  margin: 0 0 12px;
  line-height: 1.18;
}

.quick-sub {
  margin: 0;
  font-size: 17px;
  color: var(--text-muted);
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
}

.quick-card {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  background: white;
  border-radius: 20px;
  padding: 28px 30px;
  border: 1px solid #ece9e3;
  text-decoration: none;
  color: inherit;
  transition:
    transform 0.25s var(--ease-out-quart),
    box-shadow 0.25s ease,
    border-color 0.2s ease;
}

.quick-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: rgba(13, 107, 94, 0.2);
}

.quick-card:hover .quick-card-link {
  letter-spacing: 0.01em;
}

.quick-card-icon-wrap {
  width: 50px;
  height: 50px;
  min-width: 50px;
  border-radius: 14px;
  background: var(--teal-light);
  display: grid;
  place-items: center;
  font-size: 22px;
  color: var(--primary);
  flex-shrink: 0;
  transition: background 0.2s ease, transform 0.2s ease;
}

.quick-card:hover .quick-card-icon-wrap {
  background: rgba(13, 107, 94, 0.18);
  transform: scale(1.06);
}

.quick-card-title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-dark);
  line-height: 1.3;
}

.quick-card-desc {
  margin: 0 0 14px;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.quick-card-link {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
  transition: letter-spacing 0.18s ease;
}

/* ════════════════════════════════════════
   4. ACTIVE ALERT
════════════════════════════════════════ */
.alert-section {
  padding: 0 0 80px;
}

.alert-card {
  display: flex;
  gap: 28px;
  align-items: flex-start;
  background: var(--alert-bg);
  border-radius: 20px;
  padding: 38px 44px;
  border-left: 5px solid var(--alert-border);
  box-shadow: 0 2px 16px rgba(224, 115, 72, 0.1);
  transition: box-shadow 0.25s ease, transform 0.25s var(--ease-out-quart);
}

.alert-card:hover {
  box-shadow: 0 8px 32px rgba(224, 115, 72, 0.16);
  transform: translateY(-2px);
}

.alert-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: var(--alert-icon-bg);
  color: white;
  display: grid;
  place-items: center;
  font-size: 22px;
  flex-shrink: 0;
}

.alert-eyebrow {
  margin: 0 0 10px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--alert-eyebrow);
  display: flex;
  align-items: center;
  gap: 7px;
}

.alert-eyebrow::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--alert-eyebrow);
}

.alert-heading {
  margin: 0 0 10px;
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 500;
  color: var(--text-dark);
  line-height: 1.3;
}

.alert-desc {
  margin: 0 0 18px;
  font-size: 15px;
  line-height: 1.7;
  color: var(--text-body);
}

.alert-list {
  margin: 0 0 22px;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.alert-list li {
  font-size: 15px;
  color: var(--text-body);
  display: flex;
  align-items: center;
  gap: 10px;
  line-height: 1.5;
}

.alert-list li::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--alert-border);
  flex-shrink: 0;
}

.alert-cta {
  font-size: 14px;
  font-weight: 700;
  color: var(--alert-eyebrow);
  transition: letter-spacing 0.18s ease;
}

.alert-cta:hover {
  letter-spacing: 0.01em;
}

/* ════════════════════════════════════════
   5. STORY — SPLIT PANEL
════════════════════════════════════════ */
.story-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 540px;
}

.story-image-side {
  overflow: hidden;
}

.story-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.7s var(--ease-out-expo);
}

.story-image-side:hover .story-image {
  transform: scale(1.03);
}

.story-content-side {
  background: linear-gradient(155deg, #1a8a78 0%, #073d34 100%);
  padding: 72px 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.eyebrow-light {
  color: rgba(255, 255, 255, 0.68) !important;
}

.eyebrow-light::before {
  background: rgba(255, 255, 255, 0.68) !important;
}

.story-heading {
  font-family: var(--font-serif);
  font-size: 36px;
  font-weight: 500;
  line-height: 1.22;
  color: white;
  margin: 0 0 36px;
}

.story-items {
  display: flex;
  flex-direction: column;
  gap: 13px;
}

.story-item {
  display: flex;
  align-items: center;
  gap: 18px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 16px 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: background 0.22s ease, transform 0.22s var(--ease-out-quart);
  cursor: default;
}

.story-item:hover {
  background: rgba(255, 255, 255, 0.17);
  transform: translateX(4px);
}

.story-item-icon {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.16);
  display: grid;
  place-items: center;
  font-size: 17px;
  color: white;
}

.story-item-title {
  margin: 0 0 3px;
  font-size: 15px;
  font-weight: 600;
  color: white;
}

.story-item-desc {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
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
  /* Softer gradient — uses the same tones as hero but lighter start */
  background: linear-gradient(
    155deg,
    #3bbfaa 0%,
    #1a8a78 22%,
    #0d6055 55%,
    #073d34 100%
  );
  padding: 100px 0;
}

.closing-inner {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.closing-heading {
  font-family: var(--font-serif);
  font-size: 52px;
  font-weight: 500;
  color: white;
  margin: 0 0 20px;
  line-height: 1.15;
}

.closing-subtext {
  margin: 0 0 52px;
  font-size: 17px;
  line-height: 1.78;
  color: rgba(255, 255, 255, 0.74);
  max-width: 600px;
}

.closing-icons {
  display: flex;
  gap: 52px;
  justify-content: center;
  margin-bottom: 48px;
}

.closing-icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 13px;
}

.closing-icon-circle {
  width: 74px;
  height: 74px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.22);
  display: grid;
  place-items: center;
  font-size: 28px;
  color: white;
  transition: background 0.22s ease, transform 0.22s var(--ease-out-quart);
}

.closing-icon-item:hover .closing-icon-circle {
  background: rgba(255, 255, 255, 0.22);
  transform: translateY(-3px);
}

.closing-icon-label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.76);
}

.btn-closing {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: white;
  color: var(--primary-dark);
  border-radius: 999px;
  padding: 18px 40px;
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-sans);
  transition: transform 0.22s var(--ease-out-quart), box-shadow 0.22s ease;
  box-shadow: 0 4px 22px rgba(0, 0, 0, 0.2);
}

.btn-closing:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.28);
}

/* ════════════════════════════════════════
   8. FEATURE CARDS
════════════════════════════════════════ */
.features-section {
  background: var(--bg-page);
}

.feature-cards-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 26px;
  margin-top: 8px;
}

.feature-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: var(--shadow-card);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.28s ease, transform 0.28s var(--ease-out-quart);
}

.feature-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px);
}

.feature-card-image-wrap {
  position: relative;
  height: 220px;
  overflow: hidden;
}

.feature-card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-out-expo);
}

.feature-card:hover .feature-card-image {
  transform: scale(1.05);
}

.feature-card-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  background: white;
  color: var(--text-dark);
  border-radius: 999px;
  padding: 5px 14px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.feature-card-body {
  padding: 26px 28px 30px;
}

.feature-card-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--teal-light);
  display: grid;
  place-items: center;
  font-size: 18px;
  margin-bottom: 16px;
  transition: transform 0.22s var(--ease-out-quart);
}

.feature-card:hover .feature-card-icon {
  transform: scale(1.08) rotate(-3deg);
}

.feature-card-title {
  margin: 0 0 10px;
  font-family: var(--font-serif);
  font-size: 21px;
  font-weight: 500;
  color: var(--text-dark);
  line-height: 1.3;
}

.feature-card-desc {
  margin: 0 0 18px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-muted);
}

.feature-card-link {
  font-size: 14px;
  font-weight: 700;
  color: var(--primary);
  transition: letter-spacing 0.18s ease;
}

.feature-card:hover .feature-card-link {
  letter-spacing: 0.01em;
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

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 48px;
  }

  .stats-quote blockquote { font-size: 22px; }

  .quick-grid { grid-template-columns: 1fr; }

  .story-section { grid-template-columns: 1fr; }
  .story-image-side { height: 300px; }
  .story-content-side { padding: 52px 40px; }

  .guidance-grid { grid-template-columns: 1fr; gap: 40px; }

  .closing-heading { font-size: 40px; }

  .feature-cards-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .hero-section { padding: 60px 0 72px; }
  .hero-heading { font-size: 40px; }
  .hero-image { height: 300px; }

  .stats-numbers { grid-template-columns: 1fr 1fr; gap: 24px 28px; }
  .stat-value { font-size: 30px; }

  .quick-heading { font-size: 32px; }

  .alert-card {
    flex-direction: column;
    padding: 28px 22px;
    gap: 18px;
  }

  .story-content-side { padding: 40px 24px; }
  .story-heading { font-size: 28px; }

  .guidance-heading { font-size: 30px; }
  .guidance-image { height: 320px; }
  .guidance-float-badge { bottom: 14px; left: 14px; padding: 12px 14px; }

  .closing-heading { font-size: 34px; }
  .closing-icons { gap: 28px; }
  .closing-icon-circle { width: 62px; height: 62px; font-size: 24px; }
}

</style>
<style scoped>
.hero-floating-art,
.home-scroll-cue {
  display: none !important;
}

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
</style>
