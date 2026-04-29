<template>
  <div class="route-page">
    <div class="route-scroll-progress" :style="{ width: `${scrollProgress}%` }"></div>

    <section class="route-hero">
      <div class="container route-hero-inner">
        <div class="route-hero-copy reveal visible">
          <router-link to="/" class="hero-back-link">← Back to Home</router-link>
          <h1>Asthma-Safe <span>Route</span><br />Planning</h1>
          <p>
            Find the cleanest path to your destination, avoiding construction dust,
            high traffic, and pollen hotspots
          </p>
        </div>

        <div class="route-hero-art reveal visible reveal-delay-1" aria-hidden="true">
          <span class="map-emoji">🗺️</span>
          <span class="soft-orb orb-one"></span>
          <span class="soft-orb orb-two"></span>
        </div>
      </div>
    </section>

    <main class="route-main section">
      <div class="container route-main-inner">
        <section class="planner-card card reveal visible">
          <div class="planner-heading">
            <h2>Plan your route</h2>
            <p>Enter your start and destination points</p>
          </div>

          <div class="route-form-grid">
            <label class="field-group">
              <span>Starting point</span>
              <input v-model="startPoint" type="text" placeholder="Southbank, Melbourne" />
            </label>

            <label class="field-group">
              <span>Destination</span>
              <input v-model="destination" type="text" placeholder="Carlton, Melbourne" />
            </label>
          </div>

          <div class="preference-block">
            <p>Preferences</p>
            <div class="preference-pills">
              <button
                v-for="preference in preferences"
                :key="preference.key"
                type="button"
                class="preference-pill"
                :class="{ active: preference.active }"
                @click="preference.active = !preference.active"
              >
                {{ preference.label }}
              </button>
            </div>
          </div>

          <button class="btn-pill btn-primary route-submit" type="button" @click="findRoutes">
            Find Safe Routes
          </button>
        </section>

        <transition name="results-reveal">
          <section v-if="showResults" ref="resultsRef" class="route-results-grid">
            <article class="route-map-card card reveal-card">
              <div class="result-card-header">
                <div>
                  <h2>Route map</h2>
                  <p>{{ startPoint || 'Southbank' }} to {{ destination || 'Carlton' }}</p>
                </div>

                <div class="route-legend" aria-label="Map legend">
                  <span><i class="line optimal"></i> Optimal</span>
                  <span><i class="line alternative"></i> Alternative</span>
                  <span><i class="dot dust"></i> Dust zone</span>
                  <span><i class="dot pollen"></i> Pollen area</span>
                </div>
              </div>

              <div class="static-map" aria-label="Static route comparison map">
                <div class="road horizontal top-road"></div>
                <div class="road horizontal middle-road"></div>
                <div class="road horizontal bottom-road"></div>
                <div class="road vertical road-one"></div>
                <div class="road vertical road-two"></div>
                <div class="road vertical road-three"></div>
                <div class="river"></div>

                <span class="map-label swanston">Swanston St</span>
                <span class="map-label flinders">Flinders St</span>
                <span class="map-label start-label">Southbank</span>
                <span class="map-label end-label">Carlton</span>

                <span class="park park-one"></span>
                <span class="park park-two"></span>

                <span class="zone dust-zone-one"></span>
                <span class="zone dust-zone-two"></span>
                <span class="zone pollen-zone-one"></span>
                <span class="zone pollen-zone-two"></span>

                <svg class="route-svg" viewBox="0 0 900 430" preserveAspectRatio="none" aria-hidden="true">
                  <path
                    class="alternative-route"
                    d="M190 385 C90 315 120 190 285 120 C415 66 555 82 650 118 C735 154 790 148 835 92"
                  />
                  <path
                    class="optimal-route"
                    d="M190 385 L230 300 C280 208 345 138 432 108 L525 72 L640 54 L835 92"
                  />
                </svg>

                <span class="route-pin start-pin"></span>
                <span class="route-pin end-pin">◆</span>

              </div>
            </article>

            <aside class="route-options reveal-card reveal-delay-card">
              <div class="routes-found">
                <h3>3 routes found</h3>
                <p>Sorted by safety score</p>
              </div>

              <article
                v-for="route in routes"
                :key="route.name"
                class="route-option-card card"
                :class="[route.tone, { selected: selectedRoute === route.name }]"
                @click="selectedRoute = route.name"
              >
                <div class="route-option-top">
                  <h4>{{ route.name }}</h4>
                  <span class="route-tag" :class="route.tone">{{ route.tag }}</span>
                </div>

                <div class="route-stats">
                  <div>
                    <span>Time</span>
                    <strong>{{ route.time }}</strong>
                  </div>
                  <div>
                    <span>Distance</span>
                    <strong>{{ route.distance }}</strong>
                  </div>
                  <div>
                    <span>Safety</span>
                    <strong :class="route.tone">{{ route.score }}</strong>
                  </div>
                </div>

                <ul class="route-notes">
                  <li v-for="note in route.notes" :key="note" :class="route.tone">
                    {{ note }}
                  </li>
                </ul>
              </article>

              <div class="recommendation-card">
                <h4>SAFAIR recommends Route A</h4>
                <p>
                  This route avoids construction zones and minimizes exposure to traffic pollutants.
                </p>
              </div>
            </aside>
          </section>
        </transition>
      </div>
    </main>

  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, reactive, ref } from 'vue'
import DisclaimerBanner from '../components/DisclaimerBanner.vue'
import SiteFooter from '../components/SiteFooter.vue'

const startPoint = ref('Southbank, Melbourne')
const destination = ref('Carlton, Melbourne')
const showResults = ref(false)
const selectedRoute = ref('Route A — Swanston St')
const resultsRef = ref(null)
const scrollProgress = ref(0)

const preferences = reactive([
  { key: 'dust', label: 'Avoid dust zones', active: true },
  { key: 'pollen', label: 'Avoid high pollen', active: false },
  { key: 'traffic', label: 'Avoid busy roads', active: false },
  { key: 'shortest', label: 'Shortest only', active: false },
])

const routes = [
  {
    name: 'Route A — Swanston St',
    tag: 'Best',
    tone: 'best',
    time: '22 min',
    distance: '1.8 km',
    score: '8.4/10',
    notes: ['✓ Avoids all dust zones', '✓ Low traffic exposure', '✓ Passes through parks'],
  },
  {
    name: 'Route B — King St',
    tag: 'Moderate',
    tone: 'moderate',
    time: '19 min',
    distance: '1.6 km',
    score: '6.1/10',
    notes: ['✓ Shortest distance', '⚠ Passes 1 moderate dust site'],
  },
  {
    name: 'Route C — Lonsdale St',
    tag: 'Avoid',
    tone: 'avoid',
    time: '24 min',
    distance: '2.1 km',
    score: '3.8/10',
    notes: ['✕ Passes 2 high-dust sites', '✕ Heavy traffic corridor'],
  },
]

const updateScrollProgress = () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  const height = document.documentElement.scrollHeight - window.innerHeight
  scrollProgress.value = height > 0 ? Math.min((scrollTop / height) * 100, 100) : 0
}

const findRoutes = async () => {
  showResults.value = true
  await nextTick()

  if (resultsRef.value) {
    const headerOffset = 118
    const targetTop = resultsRef.value.getBoundingClientRect().top + window.scrollY - headerOffset
    window.scrollTo({ top: Math.max(targetTop, 0), behavior: 'smooth' })
  }
}

onMounted(() => {
  window.addEventListener('scroll', updateScrollProgress, { passive: true })
  updateScrollProgress()
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateScrollProgress)
})
</script>

<style scoped>
.route-page {
  background: var(--bg-page);
  color: var(--text-dark);
  overflow-x: hidden;
}

.route-scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #2b63bd, var(--primary));
  z-index: 9999;
  transition: width 0.12s ease-out;
}

.route-hero {
  position: relative;
  background: linear-gradient(135deg, #173663 0%, #2c61be 100%);
  min-height: 590px;
  color: white;
  overflow: hidden;
}

.route-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 72% 42%, rgba(255, 255, 255, 0.11), transparent 22%),
    linear-gradient(120deg, rgba(255,255,255,0.03), transparent 48%);
  pointer-events: none;
}

.route-hero-inner {
  position: relative;
  z-index: 1;
  min-height: 590px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.8fr);
  align-items: center;
  gap: 64px;
  padding-top: 26px;
}

.hero-back-link {
  display: inline-flex;
  color: rgba(255, 255, 255, 0.82);
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 26px;
  transition: transform 0.25s var(--ease-out-quart), color 0.25s ease;
}

.hero-back-link:hover {
  color: white;
  transform: translateX(-4px);
}

.route-hero-copy h1 {
  font-family: var(--font-serif);
  font-size: clamp(48px, 6vw, 78px);
  line-height: 0.95;
  font-weight: 500;
  margin: 0 0 28px;
  letter-spacing: -0.03em;
}

.route-hero-copy h1 span {
  font-style: italic;
}

.route-hero-copy p {
  max-width: 690px;
  margin: 0;
  color: rgba(255, 255, 255, 0.88);
  font-size: 20px;
  line-height: 1.55;
}

.route-hero-art {
  position: relative;
  height: 300px;
  display: grid;
  place-items: center;
}

.map-emoji {
  position: relative;
  z-index: 2;
  font-size: 56px;
  filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.22));
  animation: floatMap 4.5s ease-in-out infinite;
}

.soft-orb {
  position: absolute;
  border-radius: 38px;
  background: rgba(255, 255, 255, 0.06);
  filter: blur(1px);
}

.orb-one {
  width: 360px;
  height: 220px;
  transform: rotate(-8deg);
}

.orb-two {
  width: 210px;
  height: 150px;
  right: 20px;
  bottom: 24px;
}

.route-main {
  padding-top: 0;
  margin-top: -48px;
  position: relative;
  z-index: 2;
}

.route-main-inner {
  display: grid;
  gap: 72px;
}

.planner-card {
  padding: 36px 40px 38px;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-hover);
  transition: transform 0.35s var(--ease-out-quart), box-shadow 0.35s ease;
}

.planner-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 18px 54px rgba(10, 40, 30, 0.14);
}

.planner-heading h2,
.result-card-header h2,
.routes-found h3 {
  font-family: var(--font-serif);
  font-weight: 500;
  color: var(--text-dark);
  margin: 0;
}

.planner-heading h2 {
  font-size: 30px;
  margin-bottom: 12px;
}

.planner-heading p,
.result-card-header p,
.routes-found p {
  margin: 0;
  color: #3d4a63;
  line-height: 1.5;
}

.route-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.field-group {
  display: grid;
  gap: 11px;
}

.field-group span,
.preference-block p {
  color: var(--text-dark);
  font-weight: 700;
  font-size: 14px;
  margin: 0;
}

.field-group input {
  width: 100%;
  border: 1px solid transparent;
  background: #f7f4f0;
  border-radius: var(--radius-sm);
  padding: 18px 20px;
  font: inherit;
  font-size: 16px;
  color: var(--text-dark);
  outline: none;
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.field-group input:focus {
  background: white;
  border-color: rgba(13, 107, 94, 0.28);
  box-shadow: 0 0 0 4px var(--teal-muted);
  transform: translateY(-1px);
}

.preference-block {
  margin-top: 28px;
}

.preference-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 14px;
}

.preference-pill {
  border: none;
  border-radius: 999px;
  padding: 13px 18px;
  background: #f7f4f0;
  color: #3d4a63;
  font-weight: 600;
  transition: transform 0.25s var(--ease-out-quart), background 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
}

.preference-pill:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: var(--shadow-card);
}

.preference-pill.active {
  background: var(--teal-light);
  color: var(--primary-dark);
}

.route-submit {
  width: 100%;
  justify-content: center;
  margin-top: 26px;
  padding-block: 17px;
  font-size: 16px;
}

.route-submit:hover {
  transform: translateY(-3px) scale(1.005);
}

.route-results-grid {
  display: grid;
  grid-template-columns: minmax(720px, 2.2fr) minmax(330px, 0.8fr);
  gap: 36px;
  align-items: start;
  scroll-margin-top: 150px;
  width: 100%;
}

.route-map-card {
  overflow: hidden;
  border-radius: var(--radius-xl);
  transition: transform 0.35s var(--ease-out-quart), box-shadow 0.35s ease;
}

.route-map-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-hover);
}

.result-card-header {
  padding: 34px 38px 24px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
}

.result-card-header h2 {
  font-size: 27px;
  margin-bottom: 10px;
}

.route-legend {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 14px 18px;
  margin-top: 2px;
  color: #3d4a63;
  font-size: 13px;
  max-width: 100%;
}

.route-legend span,
.mini-legend span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.line {
  width: 20px;
  height: 3px;
  display: inline-block;
  border-radius: 999px;
}

.line.optimal { background: #0d9488; }
.line.alternative { background: #d97706; border-top: 2px dashed #d97706; height: 0; }

.dot {
  width: 12px;
  height: 12px;
  display: inline-block;
  border-radius: 50%;
}

.dot.dust { background: #e45d3e; }
.dot.pollen { background: #2f8a5e; }

.static-map {
  position: relative;
  height: clamp(560px, 48vw, 640px);
  margin: 0 38px 38px;
  background:
    radial-gradient(circle at 78% 24%, rgba(144, 176, 132, 0.18), transparent 18%),
    linear-gradient(180deg, #eaf2e8 0%, #e5eee3 100%);
  border: 1px solid rgba(10, 40, 30, 0.08);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.35);
}

.road {
  position: absolute;
  background: rgba(133, 119, 91, 0.27);
  border-radius: 999px;
}

.road.horizontal { height: 3px; width: 70%; left: 15%; }
.top-road { top: 20%; }
.middle-road { top: 44%; }
.bottom-road { top: 80%; }
.road.vertical { width: 3px; height: 100%; top: 0; }
.road-one { left: 29%; }
.road-two { left: 43%; }
.road-three { left: 58%; }

.river {
  position: absolute;
  left: 14%;
  right: 16%;
  top: 65%;
  height: 30px;
  background: rgba(112, 174, 214, 0.38);
  transform: rotate(-2deg);
  filter: blur(0.2px);
}

.map-label {
  position: absolute;
  color: #72839a;
  font-size: 12px;
  font-weight: 600;
}

.swanston { top: 48px; left: 45%; }
.flinders { top: 36%; left: 18%; }
.start-label { bottom: 34px; left: 27%; color: #344154; }
.end-label { top: 88px; right: 16%; color: #344154; }

.park,
.zone {
  position: absolute;
  display: block;
}

.park {
  border-radius: 14px;
  background: rgba(144, 176, 132, 0.25);
}

.park-one { width: 145px; height: 100px; right: 17%; top: 12%; }
.park-two { width: 125px; height: 92px; right: 22%; top: 48%; }

.zone {
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.dust-zone-one,
.dust-zone-two {
  width: 32px;
  height: 32px;
  border: 5px solid rgba(228, 93, 62, 0.8);
  background: rgba(228, 93, 62, 0.12);
}

.dust-zone-one { left: 34%; top: 57%; }
.dust-zone-two { right: 26%; top: 38%; }

.pollen-zone-one,
.pollen-zone-two {
  width: 26px;
  height: 26px;
  border: 4px solid rgba(47, 138, 94, 0.92);
  background: rgba(47, 138, 94, 0.1);
}

.pollen-zone-one { left: 50%; top: 49%; }
.pollen-zone-two { right: 20%; top: 30%; }

.route-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.optimal-route,
.alternative-route {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.optimal-route {
  stroke: #0d9488;
  stroke-width: 5;
  filter: drop-shadow(0 2px 4px rgba(13, 148, 136, 0.2));
  stroke-dasharray: 1100;
  animation: drawRoute 1.3s var(--ease-out-expo) forwards;
}

.alternative-route {
  stroke: #d97706;
  stroke-width: 3;
  stroke-dasharray: 8 10;
  animation: dashMove 1.8s linear infinite;
}

.route-pin {
  position: absolute;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: white;
  border: 5px solid #0d9488;
  transform: translate(-50%, -50%);
  box-shadow: 0 8px 20px rgba(10, 40, 30, 0.22);
  z-index: 2;
}

.start-pin { left: 27%; top: 80%; }
.end-pin {
  left: 86%;
  top: 20%;
  width: 20px;
  height: 20px;
  border: none;
  background: #2b63bd;
  color: white;
  display: grid;
  place-items: center;
  font-size: 10px;
}

.mini-legend {
  position: absolute;
  left: 24%;
  bottom: 34px;
  padding: 14px 18px;
  display: grid;
  gap: 8px;
  font-size: 11px;
  color: #334155;
  border-radius: var(--radius-sm);
  box-shadow: 0 12px 32px rgba(10, 40, 30, 0.12);
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(8px);
}

.route-options {
  display: grid;
  gap: 18px;
}

.routes-found h3 {
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.route-option-card {
  padding: 20px;
  border-radius: var(--radius-md);
  border: 2px solid transparent;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: transform 0.28s var(--ease-out-quart), box-shadow 0.28s ease, border-color 0.28s ease, background 0.28s ease;
}

.route-option-card:hover {
  transform: translateY(-5px) scale(1.015);
  box-shadow: var(--shadow-hover);
}

.route-option-card.selected,
.route-option-card.best {
  border-color: #0f9f93;
  background: #eefaf7;
}

.route-option-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 18px;
}

.route-option-top h4 {
  margin: 0;
  font-size: 17px;
  color: var(--text-dark);
}

.route-tag {
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.route-tag.best { background: var(--teal-light); color: var(--primary); }
.route-tag.moderate { background: #fff4df; color: #d97706; }
.route-tag.avoid { background: #fff0eb; color: #e24d32; }

.route-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.route-stats div {
  display: grid;
  gap: 2px;
}

.route-stats span {
  color: #728097;
  font-size: 12px;
}

.route-stats strong {
  color: var(--text-dark);
  font-size: 15px;
}

.route-stats strong.best { color: #11855c; }
.route-stats strong.moderate { color: #d97706; }
.route-stats strong.avoid { color: #e24d32; }

.route-notes {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 9px;
  font-size: 13px;
}

.route-notes li.best { color: #237856; }
.route-notes li.moderate { color: #c76d00; }
.route-notes li.avoid { color: #e24d32; }

.recommendation-card {
  background: var(--teal-light);
  border-radius: var(--radius-md);
  padding: 20px;
  transition: transform 0.28s var(--ease-out-quart), box-shadow 0.28s ease;
}

.recommendation-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card);
}

.recommendation-card h4 {
  margin: 0 0 10px;
  color: var(--text-dark);
  font-size: 16px;
}

.recommendation-card p {
  margin: 0;
  color: #3d4a63;
  line-height: 1.55;
  font-size: 13px;
}

.reveal-card {
  animation: revealUp 0.7s var(--ease-out-expo) both;
}

.reveal-delay-card {
  animation-delay: 0.12s;
}

.results-reveal-enter-active,
.results-reveal-leave-active {
  transition: opacity 0.35s ease, transform 0.35s var(--ease-out-quart);
}

.results-reveal-enter-from,
.results-reveal-leave-to {
  opacity: 0;
  transform: translateY(24px);
}

@keyframes revealUp {
  from { opacity: 0; transform: translateY(28px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes drawRoute {
  from { stroke-dashoffset: 1100; }
  to { stroke-dashoffset: 0; }
}

@keyframes dashMove {
  to { stroke-dashoffset: -36; }
}

@keyframes floatMap {
  0%, 100% { transform: translateY(0) rotate(-1deg); }
  50% { transform: translateY(-12px) rotate(2deg); }
}

@media (max-width: 1180px) {
  .route-results-grid {
    grid-template-columns: 1fr;
    gap: 26px;
  }

  .route-options {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .routes-found,
  .recommendation-card {
    grid-column: 1 / -1;
  }
}

@media (max-width: 900px) {
  .result-card-header {
    display: block;
  }

  .route-legend {
    justify-content: flex-start;
    min-width: 0;
    margin-top: 18px;
  }

  .route-hero-inner {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 72px 0 110px;
  }

  .route-hero-art {
    display: none;
  }

  .route-form-grid,
  .route-options {
    grid-template-columns: 1fr;
  }

  .planner-card {
    padding: 28px 22px;
  }

  .static-map {
    height: 480px;
    margin-inline: 20px;
  }

  .mini-legend {
    left: 22px;
    bottom: 22px;
  }
}

@media (max-width: 640px) {
  .route-hero {
    min-height: 460px;
  }

  .route-hero-inner {
    min-height: 460px;
  }

  .route-hero-copy h1 {
    font-size: 44px;
  }

  .route-hero-copy p {
    font-size: 17px;
  }

  .route-main {
    margin-top: -52px;
  }

  .route-legend {
    gap: 10px;
  }

  .route-stats {
    grid-template-columns: 1fr;
  }
}
</style>
