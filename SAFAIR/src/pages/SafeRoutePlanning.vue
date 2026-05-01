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
            <!-- Start autocomplete -->
            <div class="field-group">
              <span>Starting point</span>
              <div class="autocomplete-wrap">
                <input
                  v-model="startPoint"
                  type="text"
                  placeholder="Southbank, Melbourne"
                  autocomplete="off"
                  @input="onInput('start')"
                  @keydown.down.prevent="moveActive('start', 1)"
                  @keydown.up.prevent="moveActive('start', -1)"
                  @keydown.enter.prevent="pickActive('start')"
                  @keydown.escape="clearSuggestions('start')"
                  @blur="onBlur('start')"
                />
                <transition name="dropdown">
                  <ul v-if="startSuggestions.length" class="suggestions-list">
                    <li
                      v-for="(s, i) in startSuggestions"
                      :key="s.place_id"
                      class="suggestion-item"
                      :class="{ active: i === startActiveIdx }"
                      @mousedown.prevent="pickSuggestion('start', i)"
                    >
                      <span class="sug-icon-wrap">
                        <svg v-if="isTransit(s)" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
                        <svg v-else-if="isBuilding(s)" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
                        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C13 21.5 20 15.4 20 10a8 8 0 0 0-8-8z"/></svg>
                      </span>
                      <span class="sug-text">
                        <strong>{{ s._primary }}</strong>
                        <small>{{ s._secondary }}</small>
                      </span>
                    </li>
                  </ul>
                </transition>
              </div>
            </div>

            <div class="field-group">
              <span>Destination</span>
              <div class="autocomplete-wrap">
                <input
                  v-model="destination"
                  type="text"
                  placeholder="Carlton, Melbourne"
                  autocomplete="off"
                  @input="onInput('dest')"
                  @keydown.down.prevent="moveActive('dest', 1)"
                  @keydown.up.prevent="moveActive('dest', -1)"
                  @keydown.enter.prevent="pickActive('dest')"
                  @keydown.escape="clearSuggestions('dest')"
                  @blur="onBlur('dest')"
                />
                <transition name="dropdown">
                  <ul v-if="destSuggestions.length" class="suggestions-list">
                    <li
                      v-for="(s, i) in destSuggestions"
                      :key="s.place_id"
                      class="suggestion-item"
                      :class="{ active: i === destActiveIdx }"
                      @mousedown.prevent="pickSuggestion('dest', i)"
                    >
                      <span class="sug-icon-wrap">
                        <svg v-if="isTransit(s)" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
                        <svg v-else-if="isBuilding(s)" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
                        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C13 21.5 20 15.4 20 10a8 8 0 0 0-8-8z"/></svg>
                      </span>
                      <span class="sug-text">
                        <strong>{{ s._primary }}</strong>
                        <small>{{ s._secondary }}</small>
                      </span>
                    </li>
                  </ul>
                </transition>
              </div>
            </div>
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

          <transition name="fade">
            <div v-if="apiError" class="api-error-banner" role="alert">
              <span>⚠</span>
              <span>{{ apiError }}</span>
              <button @click="apiError = null">✕</button>
            </div>
          </transition>

          <button
            class="btn-pill btn-primary route-submit"
            type="button"
            :disabled="isLoading"
            @click="findRoutes"
          >
            <span v-if="isLoading" class="spinner" aria-hidden="true"></span>
            {{ isLoading ? 'Finding routes…' : 'Find Safe Routes' }}
          </button>
        </section>

        <transition name="results-reveal">
          <section v-if="showResults" ref="resultsRef" class="route-results-grid">

            <article class="route-map-card card reveal-card">
              <div class="result-card-header">
                <div>
                  <h2>Route map</h2>
                  <p>{{ displayStart }} to {{ displayDest }}</p>
                </div>
                <div class="route-legend" aria-label="Map legend">
                  <span><i class="line optimal"></i> Recommended</span>
                  <span><i class="line alternative"></i> Alternative</span>
                  <span><i class="dot dust"></i> Dust zone</span>
                  <span><i class="dot pollen"></i> Pollen area</span>
                </div>
              </div>

              <div ref="mapContainer" class="leaflet-map-container"></div>

              <!-- Comparison message -->

            </article>

            <aside class="route-options reveal-card reveal-delay-card">
              <div class="routes-found">
                <h3>{{ routes.length }} route{{ routes.length !== 1 ? 's' : '' }} found</h3>
                <p>Sorted by safety score</p>
              </div>

              <article
                v-for="(route, index) in routes"
                :key="route.name"
                class="route-option-card card"
                :class="[route.tone, { selected: selectedRouteIndex === index }]"
                @click="selectRoute(index)"
              >
                <div class="route-option-top">
                  <h4>{{ route.name }}</h4>
                  <span class="route-tag" :class="route.tone">{{ route.tag }}</span>
                </div>
                <div class="route-stats">
                  <div><span>Time</span><strong>{{ route.time }}</strong></div>
                  <div><span>Distance</span><strong>{{ route.distance }}</strong></div>
                  <div><span>Safety</span><strong :class="route.tone">{{ route.score }}</strong></div>
                </div>
                <ul class="route-notes">
                  <li v-for="note in route.notes" :key="note" :class="route.tone">{{ note }}</li>
                </ul>
              </article>

              <div v-if="exposureSummary.dust || exposureSummary.pollen" class="exposure-card">
                <div v-if="exposureSummary.dust" class="exposure-row dust-row">
                  <span class="exp-icon">🏗</span>
                  <div>
                    <strong>{{ exposureSummary.dust.label }}</strong>
                    <p>{{ exposureSummary.dust.detail }}</p>
                  </div>
                </div>
                <div v-if="exposureSummary.pollen" class="exposure-row pollen-row">
                  <span class="exp-icon">🌿</span>
                  <div>
                    <strong>{{ exposureSummary.pollen.label }}</strong>
                    <p>{{ exposureSummary.pollen.detail }}</p>
                  </div>
                </div>
              </div>

              <div v-if="recommendedName" class="recommendation-card">
                <h4>BRTHEZ recommends {{ recommendedName }}</h4>
                <p>{{ recommendationReason }}</p>
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

const API_BASE = 'http://13.239.20.161'

const SUBURB_COORDS = {
  'Melbourne':       { lat: -37.8136, lon: 144.9631 },
  'Southbank':       { lat: -37.8230, lon: 144.9650 },
  'Docklands':       { lat: -37.8145, lon: 144.9460 },
  'Carlton':         { lat: -37.8000, lon: 144.9670 },
  'North Melbourne': { lat: -37.7990, lon: 144.9430 },
  'West Melbourne':  { lat: -37.8080, lon: 144.9380 },
  'East Melbourne':  { lat: -37.8160, lon: 144.9870 },
  'Parkville':       { lat: -37.7860, lon: 144.9550 },
  'Kensington':      { lat: -37.7940, lon: 144.9260 },
  'South Yarra':     { lat: -37.8380, lon: 144.9930 },
}

const startPoint   = ref('Southbank, Melbourne')
const destination  = ref('Carlton, Melbourne')
const showResults    = ref(false)
const displayStart   = ref('Southbank, Melbourne')
const displayDest    = ref('Carlton, Melbourne')
const selectedRouteIndex = ref(0)
const resultsRef   = ref(null)
const mapContainer = ref(null)
const scrollProgress = ref(0)
const isLoading    = ref(false)
const apiError     = ref(null)
const comparisonMessage    = ref(null)
const recommendedName      = ref(null)
const recommendationReason = ref('')
const routes          = ref([])
const exposureSummary = ref({ dust: null, pollen: null })
const routeGeometries = ref([])
const dustZones       = ref([])
const pollenZones     = ref([])

// Leaflet kept outside Vue reactivity
let leafletMap  = null
let routeLayers = []
let zoneLayers  = []

const preferences = reactive([
  { key: 'dust',     label: 'Avoid dust zones',  active: true  },
  { key: 'pollen',   label: 'Avoid high pollen', active: false },
  { key: 'traffic',  label: 'Avoid busy roads',  active: false },
  { key: 'shortest', label: 'Shortest only',     active: false },
])

const startSuggestions = ref([])
const destSuggestions  = ref([])
const startActiveIdx   = ref(-1)
const destActiveIdx    = ref(-1)
let startTimer = null
let destTimer  = null

async function fetchSuggestions(query) {
  if (!query || query.length < 2) return []
  try {
    const url = new URL('https://nominatim.openstreetmap.org/search')
    url.searchParams.set('q', query)
    url.searchParams.set('countrycodes', 'au')
    url.searchParams.set('limit', '6')
    url.searchParams.set('format', 'json')
    url.searchParams.set('addressdetails', '1')
    url.searchParams.set('extratags', '1')
    // Bias results toward Melbourne CBD
    url.searchParams.set('viewbox', '144.85,-37.95,145.15,-37.70')
    url.searchParams.set('bounded', '0')
    const res = await fetch(url.toString(), {
      headers: { 'Accept-Language': 'en', 'User-Agent': 'AsthmaSafe/1.0' },
    })
    const data = await res.json()
    
    return data.map(r => {
      const a = r.address || {}
      const primary =
        a.amenity || a.building || a.shop || a.tourism ||
        a.leisure || a.office || a.stadium ||
        (a.house_number && a.road ? `${a.house_number} ${a.road}` : null) ||
        a.road || a.suburb || a.city_district ||
        r.display_name.split(',')[0]
      const suburb  = a.suburb || a.city_district || a.neighbourhood || ''
      const state   = a.state_district || a.state || ''
      const postcode = a.postcode || ''
      const secondary = [suburb, state, postcode].filter(Boolean).join(', ')
      return { ...r, _primary: primary, _secondary: secondary }
    })
  } catch { return [] }
}

function isTransit(s) {
  const t = s.type || ''
  const c = s.class || ''
  return ['station', 'stop', 'tram_stop', 'bus_stop', 'subway'].includes(t) || c === 'railway' || c === 'public_transport'
}
function isBuilding(s) {
  const t = s.type || ''
  const c = s.class || ''
  return ['university', 'school', 'hospital', 'hotel', 'restaurant', 'cafe', 'shop', 'building', 'amenity'].includes(t) || c === 'amenity' || c === 'building' || c === 'tourism'
}

function onInput(field) {
  const isStart = field === 'start'
  const query   = isStart ? startPoint.value : destination.value
  clearTimeout(isStart ? startTimer : destTimer)

  if (!query || query.length < 2) {
    isStart ? (startSuggestions.value = []) : (destSuggestions.value = [])
    return
  }
  const t = setTimeout(async () => {
    const results = await fetchSuggestions(query)
    if (isStart) { startSuggestions.value = results; startActiveIdx.value = -1 }
    else         { destSuggestions.value  = results; destActiveIdx.value  = -1 }
  }, 300)
  isStart ? (startTimer = t) : (destTimer = t)
}

function moveActive(field, dir) {
  const isStart = field === 'start'
  const list = isStart ? startSuggestions.value : destSuggestions.value
  const cur  = isStart ? startActiveIdx.value   : destActiveIdx.value
  const next = Math.max(-1, Math.min(list.length - 1, cur + dir))
  isStart ? (startActiveIdx.value = next) : (destActiveIdx.value = next)
}

function pickActive(field) {
  const idx = field === 'start' ? startActiveIdx.value : destActiveIdx.value
  if (idx >= 0) pickSuggestion(field, idx)
}

function pickSuggestion(field, index) {
  const isStart = field === 'start'
  const item    = (isStart ? startSuggestions.value : destSuggestions.value)[index]
  if (!item) return
  const name = item._secondary
    ? `${item._primary}, ${item._secondary}`
    : item._primary
  if (isStart) { startPoint.value = name; startSuggestions.value = []; startActiveIdx.value = -1 }
  else         { destination.value = name; destSuggestions.value = []; destActiveIdx.value = -1 }
}

function clearSuggestions(field) {
  if (field === 'start') { startSuggestions.value = []; startActiveIdx.value = -1 }
  else                   { destSuggestions.value  = []; destActiveIdx.value  = -1 }
}

function onBlur(field) {
  setTimeout(() => clearSuggestions(field), 150)
}

async function geocode(address) {
  try {
    const url = new URL('https://nominatim.openstreetmap.org/search')
    url.searchParams.set('q', address)
    url.searchParams.set('countrycodes', 'au')
    url.searchParams.set('limit', '1')
    url.searchParams.set('format', 'json')
    const res  = await fetch(url.toString(), {
      headers: { 'Accept-Language': 'en', 'User-Agent': 'AsthmaSafe/1.0' },
    })
    const data = await res.json()
    if (data?.length > 0)
      return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) }
  } catch { /* fall through */ }
  return null
}

function buildWeights() {
  if (preferences.find(p => p.key === 'shortest')?.active)
    return { w_dist: 1.0, w_dust: 0.0, w_pollen: 0.0 }
  const avoidDust   = preferences.find(p => p.key === 'dust')?.active   ? 0.35 : 0.15
  const avoidPollen = preferences.find(p => p.key === 'pollen')?.active ? 0.35 : 0.15
  const dist  = Math.max(0.1, 1.0 - avoidDust - avoidPollen)
  const total = dist + avoidDust + avoidPollen
  return {
    w_dist:   +(dist        / total).toFixed(3),
    w_dust:   +(avoidDust   / total).toFixed(3),
    w_pollen: +(avoidPollen / total).toFixed(3),
  }
}

function scoreToTone(score) {
  return score <= 35 ? 'best' : score <= 65 ? 'moderate' : 'avoid'
}

function shapeRoute(raw, index, isRec) {
  const tone = isRec ? 'best' : scoreToTone(raw.composite_score ?? 50)
  const safetyDisplay = raw.safety_score != null
    ? `${Math.round(raw.safety_score * 10) / 10}/10`
    : `${Math.round(100 - (raw.composite_score ?? 50))}/100`
  const notes = []
  if (raw.scores?.raw_dust   != null)
    notes.push(raw.scores.raw_dust   < 30 ? '✓ Low dust exposure'   : '⚠ Elevated dust along route')
  if (raw.scores?.raw_pollen != null)
    notes.push(raw.scores.raw_pollen < 30 ? '✓ Low pollen exposure' : '⚠ Elevated pollen along route')
  if (isRec) notes.unshift('✓ Recommended by BRTHEZ')
  return {
    name:     ['Route A', 'Route B', 'Route C', 'Route D'][index] ?? `Route ${index + 1}`,
    tag:      { best: 'Best', moderate: 'Moderate', avoid: 'Avoid' }[tone] ?? 'Moderate',
    tone,
    time:     `${Math.round(raw.duration_min ?? 0)} min`,
    distance: raw.distance_m >= 1000
      ? `${(raw.distance_m / 1000).toFixed(1)} km`
      : `${Math.round(raw.distance_m ?? 0)} m`,
    score: safetyDisplay,
    notes,
  }
}

function buildZones(allRaw, metadata) {
  const dust = []; const pollen = []
  const allCoords = allRaw.flatMap(r =>
    (r?.geometry?.coordinates ?? []).map(([lon, lat]) => ({ lat, lon }))
  )
  if (!allCoords.length) return { dust, pollen }
  const lats   = allCoords.map(c => c.lat)
  const lons   = allCoords.map(c => c.lon)
  const minLat = Math.min(...lats) - 0.015
  const maxLat = Math.max(...lats) + 0.015
  const minLon = Math.min(...lons) - 0.015
  const maxLon = Math.max(...lons) + 0.015
  const rawDust = allRaw[0]?.scores?.raw_dust ?? 0
  for (const [name, coords] of Object.entries(SUBURB_COORDS)) {
    if (coords.lat >= minLat && coords.lat <= maxLat && coords.lon >= minLon && coords.lon <= maxLon) {
      const intensity = rawDust > 0 ? Math.min(rawDust / 500000, 1) : 0.3
      dust.push({ lat: coords.lat, lon: coords.lon, radius: 180 + intensity * 220, label: name })
    }
  }
  if ((metadata?.pollen_season ?? []).length > 0 && (metadata?.trees_found ?? 0) > 0) {
    const midLat = (Math.min(...lats) + Math.max(...lats)) / 2
    const midLon = (Math.min(...lons) + Math.max(...lons)) / 2
    pollen.push({ lat: midLat + 0.003, lon: midLon - 0.002, radius: 120 })
    pollen.push({ lat: midLat - 0.004, lon: midLon + 0.005, radius: 90  })
  }
  return { dust, pollen }
}

function buildExposureSummary(raw, metadata) {
  const summary = { dust: null, pollen: null }
  const rawDust      = raw?.scores?.raw_dust ?? 0
  const permitsFound = metadata?.permits_found ?? 0
  if (permitsFound > 0) {
    const level = rawDust < 100000 ? 'Low' : rawDust < 500000 ? 'Moderate' : 'High'
    summary.dust = {
      label:  `${level} dust risk`,
      detail: `${permitsFound} active construction permit${permitsFound !== 1 ? 's' : ''} near this route`,
    }
  }
  const season = metadata?.pollen_season ?? []
  summary.pollen = season.length > 0
    ? { label: `${(raw?.scores?.raw_pollen ?? 0) < 50 ? 'Low' : 'Moderate'} pollen`, detail: `Active genera: ${season.slice(0, 3).join(', ')}` }
    : { label: 'Low pollen', detail: 'No allergenic trees currently in season' }
  return summary
}

function loadLeaflet() {
  return new Promise(resolve => {
    if (window.L) return resolve(window.L)
    const link = document.createElement('link')
    link.rel  = 'stylesheet'
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    document.head.appendChild(link)
    const script  = document.createElement('script')
    script.src    = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
    script.onload = () => resolve(window.L)
    document.head.appendChild(script)
  })
}

async function initMap(centerLat, centerLon) {
  const L = await loadLeaflet()
  if (leafletMap) { leafletMap.remove(); leafletMap = null; routeLayers = []; zoneLayers = [] }
  leafletMap = L.map(mapContainer.value, { zoomControl: true }).setView([centerLat, centerLon], 14)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OSM</a> © <a href="https://carto.com/">CARTO</a>',
    maxZoom: 19,
  }).addTo(leafletMap)
  return L
}

function drawZones() {
  if (!leafletMap) return
  const L = window.L
  zoneLayers.forEach(l => leafletMap.removeLayer(l))
  zoneLayers = []
  dustZones.value.forEach(z => {
    const c = L.circle([z.lat, z.lon], {
      radius: z.radius, color: '#e45d3e', fillColor: '#e45d3e',
      fillOpacity: 0.12, weight: 2, dashArray: '5 6',
    }).addTo(leafletMap)
    c.bindTooltip(`🏗 Dust zone — ${z.label}`, { sticky: true, className: 'zone-tip' })
    zoneLayers.push(c)
  })
  pollenZones.value.forEach(z => {
    const c = L.circle([z.lat, z.lon], {
      radius: z.radius, color: '#2f8a5e', fillColor: '#2f8a5e',
      fillOpacity: 0.15, weight: 2, dashArray: '5 6',
    }).addTo(leafletMap)
    c.bindTooltip('🌿 Pollen zone', { sticky: true, className: 'zone-tip' })
    zoneLayers.push(c)
  })
}

// Tone → map colour mapping
const TONE_COLORS = {
  best:     '#0d9488',   // teal  — safest
  moderate: '#d97706',   // amber — moderate
  avoid:    '#dc2626',   // red   — avoid
}

async function drawRoutes(selectedIdx) {
  if (!leafletMap || !routeGeometries.value.length) return
  const L = window.L
  routeLayers.forEach(l => leafletMap.removeLayer(l))
  routeLayers = []

  const selectedColor = TONE_COLORS[routes.value[selectedIdx]?.tone] ?? '#0d9488'

  // Non-selected routes — grey dashed
  routeGeometries.value.forEach((geom, idx) => {
    if (idx === selectedIdx || !geom?.coordinates?.length) return
    const ll = geom.coordinates.map(([lon, lat]) => [lat, lon])
    routeLayers.push(
      L.polyline(ll, { color: '#94a3b8', weight: 3, opacity: 0.45, dashArray: '8 10' }).addTo(leafletMap)
    )
  })

  const sel = routeGeometries.value[selectedIdx]
  if (sel?.coordinates?.length) {
    const ll = sel.coordinates.map(([lon, lat]) => [lat, lon])

    // Glow uses selected route colour
    const glow = L.polyline(ll, { color: selectedColor, weight: 16, opacity: 0.08 }).addTo(leafletMap)
    const line = L.polyline(ll, {
      color: selectedColor, weight: 5, opacity: 1, lineJoin: 'round', lineCap: 'round',
    }).addTo(leafletMap)

    // Start pin — white circle with selected colour border
    const startIcon = L.divIcon({
      className: '',
      html: `<div style="width:14px;height:14px;border-radius:50%;background:white;border:4px solid ${selectedColor};box-shadow:0 4px 12px rgba(10,40,30,0.22);"></div>`,
      iconAnchor: [7, 7],
    })
    // End pin — selected colour diamond
    const endIcon = L.divIcon({
      className: '',
      html: `<div style="width:14px;height:14px;border-radius:3px;background:${selectedColor};border:2.5px solid white;box-shadow:0 4px 12px rgba(10,40,30,0.22);transform:rotate(45deg);"></div>`,
      iconAnchor: [7, 7],
    })

    const sm = L.marker(ll[0], { icon: startIcon }).addTo(leafletMap)
      .bindPopup(`<div class="map-popup"><strong>Start</strong><br>${startPoint.value}</div>`)
    const em = L.marker(ll[ll.length - 1], { icon: endIcon }).addTo(leafletMap)
      .bindPopup(`<div class="map-popup"><strong>Destination</strong><br>${destination.value}</div>`)

    routeLayers.push(glow, line, sm, em)
    leafletMap.fitBounds(line.getBounds(), { padding: [48, 48] })
  }
}

function selectRoute(index) {
  selectedRouteIndex.value = index
  drawRoutes(index)
}

async function findRoutes() {
  apiError.value = null
  comparisonMessage.value = null
  isLoading.value = true

  try {
    const [sc, ec] = await Promise.all([geocode(startPoint.value), geocode(destination.value)])
    if (!sc) throw new Error(`Could not locate "${startPoint.value}". Try a more specific address.`)
    if (!ec) throw new Error(`Could not locate "${destination.value}". Try a more specific address.`)

    const params = new URLSearchParams({
      start_lat: sc.lat, start_lon: sc.lon,
      end_lat: ec.lat,   end_lon: ec.lon,
      profile: 'walking', ...buildWeights(),
    })

    const res = await fetch(`${API_BASE}/api/route-compare?${params}`)
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error ?? `API error ${res.status}`)
    const data = await res.json()
    if (!data.success) throw new Error(data.error ?? 'Unknown error')

    const allRaw = [data.recommended]
    if (data.comparison && !data.comparison.is_same_route && data.shortest)
      allRaw.push(data.shortest)

    routeGeometries.value = allRaw.filter(r => r?.geometry?.coordinates?.length).map(r => r.geometry)
    routes.value          = allRaw.map((r, i) => shapeRoute(r, i, i === 0))
    selectedRouteIndex.value = 0
    recommendedName.value    = routes.value[0]?.name ?? null

    if (data.comparison && !data.comparison.is_same_route) {
      comparisonMessage.value    = data.comparison.message
      recommendationReason.value = data.comparison.message
    } else {
      recommendationReason.value = 'This route avoids construction zones and minimises exposure to traffic pollutants.'
    }

    const zones = buildZones(allRaw, data.metadata)
    dustZones.value       = zones.dust
    pollenZones.value     = zones.pollen
    exposureSummary.value = buildExposureSummary(data.recommended, data.metadata)

    displayStart.value = startPoint.value
    displayDest.value  = destination.value
    showResults.value  = true
    await nextTick()

    if (resultsRef.value) {
      const top = resultsRef.value.getBoundingClientRect().top + window.scrollY - 118
      window.scrollTo({ top: Math.max(top, 0), behavior: 'smooth' })
    }

    await new Promise(r => setTimeout(r, 150))

    const coords = routeGeometries.value[0]?.coordinates ?? []
    const mid    = coords[Math.floor(coords.length / 2)]
    await initMap(mid ? mid[1] : sc.lat, mid ? mid[0] : sc.lon)
    drawZones()
    await drawRoutes(0)

  } catch (err) {
    apiError.value = err.message ?? 'Something went wrong. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const updateScrollProgress = () => {
  const h = document.documentElement.scrollHeight - window.innerHeight
  scrollProgress.value = h > 0 ? Math.min((window.scrollY / h) * 100, 100) : 0
}
onMounted(() => { window.addEventListener('scroll', updateScrollProgress, { passive: true }); updateScrollProgress() })
onUnmounted(() => { window.removeEventListener('scroll', updateScrollProgress); if (leafletMap) leafletMap.remove() })
</script>

<style scoped>
.route-page {
  background: var(--bg-page);
  color: var(--text-dark);
  overflow-x: hidden;
}

.route-scroll-progress { display: none; }

/* ── Hero ──────────────────────────────────────────────────── */
.route-hero {
  position: relative;
  background: linear-gradient(135deg, #173663 0%, #2c61be 100%);
  min-height: 590px;
  color: white;
  overflow: hidden;
}
.route-hero::after {
  content: '';
  position: absolute; inset: 0;
  background:
    radial-gradient(circle at 72% 42%, rgba(255,255,255,0.11), transparent 22%),
    linear-gradient(120deg, rgba(255,255,255,0.03), transparent 48%);
  pointer-events: none;
}
.route-hero-inner {
  position: relative; z-index: 1;
  min-height: 590px;
  display: grid;
  grid-template-columns: minmax(0,1fr) minmax(280px,0.8fr);
  align-items: center;
  gap: 64px;
  padding-top: 26px;
}
.hero-back-link {
  display: inline-flex;
  color: rgba(255,255,255,0.82);
  font-size: 15px; font-weight: 500;
  margin-bottom: 26px;
  transition: transform 0.25s var(--ease-out-quart), color 0.25s ease;
}
.hero-back-link:hover { color: white; transform: translateX(-4px); }

.route-hero-copy h1 {
  font-family: var(--font-serif);
  font-size: clamp(48px, 6vw, 78px);
  line-height: 0.95; font-weight: 500;
  margin: 0 0 28px; letter-spacing: -0.03em;
}
.route-hero-copy h1 span { font-style: italic; }
.route-hero-copy p {
  max-width: 690px; margin: 0;
  color: rgba(255,255,255,0.88);
  font-size: 20px; line-height: 1.55;
}

.route-hero-art {
  position: relative; height: 300px;
  display: grid; place-items: center;
}
.map-emoji {
  position: relative; z-index: 2;
  font-size: 100px;
  filter: drop-shadow(0 20px 40px rgba(0,0,0,0.22));
  animation: floatMap 4.5s ease-in-out infinite;
}
.soft-orb {
  position: absolute; border-radius: 38px;
  background: rgba(255,255,255,0.06); filter: blur(1px);
}
.orb-one { width: 360px; height: 220px; transform: rotate(-8deg); }
.orb-two { width: 210px; height: 150px; right: 20px; bottom: 24px; }

/* ── Main ──────────────────────────────────────────────────── */
.route-main { padding-top: 0; margin-top: -48px; position: relative; z-index: 2; }
.route-main-inner { display: grid; gap: 72px; }

/* ── Planner card ──────────────────────────────────────────── */
.planner-card {
  padding: 36px 40px 38px;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-hover);
  transition: transform 0.35s var(--ease-out-quart), box-shadow 0.35s ease;
}
.planner-card:hover { transform: translateY(-5px); box-shadow: 0 18px 54px rgba(10,40,30,0.14); }
.planner-heading h2 {
  font-family: var(--font-serif); font-weight: 500; font-size: 30px;
  color: var(--text-dark); margin: 0 0 12px;
}
.planner-heading p { margin: 0; color: #3d4a63; line-height: 1.5; }

/* ── Form grid ─────────────────────────────────────────────── */
.route-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0,1fr));
  gap: 20px; margin-top: 30px;
}
.field-group { display: grid; gap: 11px; }
.field-group > span {
  color: var(--text-dark); font-weight: 700; font-size: 14px; margin: 0;
}

/* ── Autocomplete ──────────────────────────────────────────── */
.autocomplete-wrap { position: relative; }

.autocomplete-wrap input {
  width: 100%; box-sizing: border-box;
  border: 1px solid transparent;
  background: #f7f4f0;
  border-radius: var(--radius-sm);
  padding: 18px 20px;
  font: inherit; font-size: 16px;
  color: var(--text-dark); outline: none;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.autocomplete-wrap input:focus {
  background: white;
  border-color: rgba(13,107,94,0.28);
  box-shadow: 0 0 0 4px var(--teal-muted, rgba(13,148,136,0.1));
  transform: translateY(-1px);
}
.autocomplete-wrap input::placeholder { color: #9aabb8; }

.suggestions-list {
  position: absolute; top: calc(100% + 8px); left: 0; right: 0;
  background: white;
  border: 1px solid rgba(10,40,30,0.1);
  border-radius: var(--radius-md, 12px);
  box-shadow: 0 16px 48px rgba(10,40,30,0.14);
  list-style: none; margin: 0; padding: 6px;
  z-index: 9999; max-height: 260px; overflow-y: auto;
}
.suggestion-item {
  display: flex; align-items: center; gap: 12px;
  padding: 8px 10px; border-radius: var(--radius-sm, 8px);
  cursor: pointer; transition: background 0.14s;
}
.suggestion-item:hover,
.suggestion-item.active { background: var(--teal-light, #e6f7f5); }
.sug-icon-wrap {
  width: 32px; height: 32px; border-radius: 50%;
  background: #f0f4f8; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  color: #546e8a;
}
.suggestion-item.active .sug-icon-wrap,
.suggestion-item:hover .sug-icon-wrap {
  background: var(--teal-light); color: var(--primary-dark, #0d6b5e);
}
.sug-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.sug-text strong { font-size: 14px; font-weight: 600; color: var(--text-dark); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
.sug-text small   { font-size: 12px; color: #8a9ab0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; margin-top: 1px; }

.dropdown-enter-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.dropdown-enter-from   { opacity: 0; transform: translateY(-6px); }

/* ── Preferences ───────────────────────────────────────────── */
.preference-block { margin-top: 28px; }
.preference-block > p {
  color: var(--text-dark); font-weight: 700; font-size: 14px; margin: 0 0 14px;
}
.preference-pills { display: flex; flex-wrap: wrap; gap: 12px; }
.preference-pill {
  border: none; border-radius: 999px;
  padding: 13px 18px; background: #f7f4f0;
  color: #3d4a63; font-weight: 600;
  transition: transform 0.25s var(--ease-out-quart), background 0.25s, color 0.25s, box-shadow 0.25s;
}
.preference-pill:hover { transform: translateY(-3px) scale(1.02); box-shadow: var(--shadow-card); }
.preference-pill.active { background: var(--teal-light); color: var(--primary-dark); }

/* ── Error banner ──────────────────────────────────────────── */
.api-error-banner {
  display: flex; align-items: center; gap: 10px;
  background: #fff0eb; border: 1.5px solid #e24d32;
  border-radius: var(--radius-sm); padding: 14px 18px; margin-top: 20px;
  font-size: 14px; color: #b83215;
}
.api-error-banner button { margin-left: auto; background: none; border: none; cursor: pointer; color: #b83215; font-size: 14px; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }

/* ── Submit button ─────────────────────────────────────────── */
@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  display: inline-block; width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,0.35); border-top-color: white;
  border-radius: 50%; animation: spin 0.7s linear infinite;
  vertical-align: middle; margin-right: 8px;
}
.btn-pill {
  padding: 16px 32px; border-radius: 999px;
  font-size: 16px; font-weight: 700; border: none; cursor: pointer;
  transition: transform 0.25s var(--ease-out-quart), box-shadow 0.25s ease, opacity 0.2s;
}
.btn-primary {
  background: var(--primary); color: white;
  box-shadow: 0 6px 24px rgba(43,99,189,0.28);
}
.btn-primary:not(:disabled):hover { transform: translateY(-3px) scale(1.005); box-shadow: 0 12px 36px rgba(43,99,189,0.38); }
.btn-primary:disabled { opacity: 0.68; cursor: not-allowed; }
.route-submit { width: 100%; justify-content: center; margin-top: 26px; padding-block: 17px; }

/* ── Results grid ──────────────────────────────────────────── */
.route-results-grid {
  display: grid;
  grid-template-columns: minmax(0, 2.2fr) minmax(330px, 0.8fr);
  gap: 36px; align-items: start;
  scroll-margin-top: 150px;
}

/* ── Map card ──────────────────────────────────────────────── */
.route-map-card {
  overflow: hidden; border-radius: var(--radius-xl);
  transition: transform 0.35s var(--ease-out-quart), box-shadow 0.35s ease;
}
.route-map-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-hover); }

.result-card-header {
  padding: 34px 38px 24px;
  display: grid; gap: 18px;
}
.result-card-header h2 {
  font-family: var(--font-serif); font-weight: 500; font-size: 27px;
  color: var(--text-dark); margin: 0 0 10px;
}
.result-card-header p { margin: 0; color: #3d4a63; }

.route-legend {
  display: flex; align-items: center; flex-wrap: wrap;
  gap: 14px 18px; color: #3d4a63; font-size: 13px;
}
.route-legend span { display: inline-flex; align-items: center; gap: 8px; }
.line { width: 20px; height: 3px; display: inline-block; border-radius: 999px; }
.line.optimal     { background: #0d9488; }
.line.alternative { background: #d97706; }
.dot  { width: 12px; height: 12px; display: inline-block; border-radius: 50%; }
.dot.dust   { background: #e45d3e; }
.dot.pollen { background: #2f8a5e; }

/* ── Leaflet map ───────────────────────────────────────────── */
.leaflet-map-container {
  width: 100%;
  height: clamp(420px, 46vw, 580px);
  margin: 0 38px 28px;
  width: calc(100% - 76px);
  border-radius: var(--radius-lg);
  overflow: hidden; position: relative; z-index: 0;
  box-shadow: 0 2px 16px rgba(10,40,30,0.08), inset 0 0 0 1px rgba(10,40,30,0.06);
}

/* ── Comparison banner ─────────────────────────────────────── */
.comparison-banner {
  display: flex; align-items: flex-start; gap: 10px;
  margin: 18px 38px 30px;
  background: var(--teal-light, #e6f7f5);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  font-size: 13px; color: #0f5349; line-height: 1.55;
}

/* ── Sidebar ───────────────────────────────────────────────── */
.route-options { display: grid; gap: 18px; }
.routes-found h3 {
  font-family: var(--font-sans); font-size: 20px; font-weight: 700;
  color: var(--text-dark); margin: 0 0 4px;
}
.routes-found p { margin: 0; color: #3d4a63; }

/* ── Route option cards ────────────────────────────────────── */
.route-option-card {
  padding: 20px; border-radius: var(--radius-md);
  border: 2px solid transparent; box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: transform 0.28s var(--ease-out-quart), box-shadow 0.28s ease, border-color 0.28s ease, background 0.28s ease;
}
.route-option-card:hover { transform: translateY(-5px) scale(1.015); box-shadow: var(--shadow-hover); }
/* Selected state — colour matches the route tone */
.route-option-card.selected {
  box-shadow: 0 8px 32px rgba(0,0,0,0.13);
  transform: translateY(-3px) scale(1.01);
}
.route-option-card.selected.best     { border-color: #0d9488; background: #e6faf7; }
.route-option-card.selected.moderate { border-color: #d97706; background: #fef3dc; }
.route-option-card.selected.avoid    { border-color: #dc2626; background: #fee8e8; }

.route-option-top {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 14px; margin-bottom: 18px;
}
.route-option-top h4 { margin: 0; font-size: 17px; color: var(--text-dark); }

.route-tag { padding: 7px 12px; border-radius: 999px; font-size: 12px; font-weight: 800; }
.route-tag.best     { background: var(--teal-light); color: var(--primary); }
.route-tag.moderate { background: #fff4df; color: #d97706; }
.route-tag.avoid    { background: #fff0eb; color: #e24d32; }

.route-stats { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 16px; }
.route-stats div    { display: grid; gap: 2px; }
.route-stats span   { color: #728097; font-size: 12px; }
.route-stats strong { color: var(--text-dark); font-size: 15px; }
.route-stats strong.best     { color: #11855c; }
.route-stats strong.moderate { color: #d97706; }
.route-stats strong.avoid    { color: #e24d32; }

.route-notes { list-style: none; margin: 0; padding: 0; display: grid; gap: 9px; font-size: 13px; }
.route-notes li.best     { color: #237856; }
.route-notes li.moderate { color: #c76d00; }
.route-notes li.avoid    { color: #e24d32; }

/* ── Exposure summary card ─────────────────────────────────── */
.exposure-card {
  background: white; border-radius: var(--radius-md);
  border: 1px solid rgba(10,40,30,0.08);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.exposure-row {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 16px 18px;
}
.exposure-row + .exposure-row { border-top: 1px solid rgba(10,40,30,0.06); }
.dust-row   { background: #fff9f5; }
.pollen-row { background: #f5fbf7; }
.exp-icon   { font-size: 18px; flex-shrink: 0; margin-top: 1px; }
.exposure-row strong { display: block; font-size: 14px; font-weight: 700; color: var(--text-dark); margin-bottom: 3px; }
.exposure-row p      { margin: 0; font-size: 12px; color: #728097; line-height: 1.4; }

/* ── Recommendation card ───────────────────────────────────── */
.recommendation-card {
  background: linear-gradient(135deg, #e6faf7 0%, #eff6ff 100%);
  border: 2px solid #0d9488;
  border-radius: var(--radius-md); padding: 20px 22px;
  box-shadow: 0 4px 20px rgba(13,148,136,0.15);
  transition: transform 0.28s var(--ease-out-quart), box-shadow 0.28s ease;
}
.recommendation-card:hover { transform: translateY(-3px); box-shadow: 0 8px 28px rgba(13,148,136,0.2); }
.recommendation-card h4 {
  margin: 0 0 8px; font-size: 15px; font-weight: 800;
  color: #0d6b5e; letter-spacing: 0.01em;
}
.recommendation-card p  { margin: 0; color: #1e4a43; line-height: 1.55; font-size: 13px; font-weight: 500; }

/* ── Animations ────────────────────────────────────────────── */
.reveal-card      { animation: revealUp 0.7s var(--ease-out-expo) both; }
.reveal-delay-card { animation-delay: 0.12s; }

.results-reveal-enter-active, .results-reveal-leave-active {
  transition: opacity 0.35s ease, transform 0.35s var(--ease-out-quart);
}
.results-reveal-enter-from, .results-reveal-leave-to {
  opacity: 0; transform: translateY(24px);
}

@keyframes revealUp  { from { opacity:0; transform:translateY(28px); } to { opacity:1; transform:translateY(0); } }
@keyframes floatMap  { 0%,100%{transform:translateY(0) rotate(-1deg);} 50%{transform:translateY(-12px) rotate(2deg);} }

/* ── Responsive ────────────────────────────────────────────── */
@media (max-width: 1180px) {
  .route-results-grid { grid-template-columns: 1fr; gap: 26px; }
  .route-options { grid-template-columns: repeat(3, minmax(0,1fr)); }
  .routes-found, .recommendation-card, .exposure-card { grid-column: 1 / -1; }
}
@media (max-width: 900px) {
  .result-card-header { display: block; }
  .route-legend { justify-content: flex-start; margin-top: 18px; }
  .route-hero-inner { grid-template-columns: 1fr; gap: 20px; padding: 72px 0 110px; }
  .route-hero-art { display: none; }
  .route-form-grid, .route-options { grid-template-columns: 1fr; }
  .planner-card { padding: 28px 22px; }
  .leaflet-map-container { height: 360px; margin: 0 20px; width: calc(100% - 40px); }
  .comparison-banner { margin: 14px 20px 24px; }
}
@media (max-width: 640px) {
  .route-hero { min-height: 460px; }
  .route-hero-inner { min-height: 460px; }
  .route-hero-copy h1 { font-size: 44px; }
  .route-hero-copy p  { font-size: 17px; }
  .route-main { margin-top: -52px; }
  .route-legend { gap: 10px; }
  .route-stats { grid-template-columns: 1fr; }
  .leaflet-map-container { height: 280px; margin: 0 16px; width: calc(100% - 32px); }
}
</style>

<!-- Global Leaflet overrides (cannot be scoped) -->
<style>
.zone-tip {
  background: white !important;
  border: 1px solid rgba(10,40,30,0.12) !important;
  border-radius: 8px !important;
  font-size: 12px !important;
  color: #334155 !important;
  box-shadow: 0 8px 24px rgba(10,40,30,0.12) !important;
  padding: 5px 10px !important;
}
.zone-tip::before { display: none !important; }
.map-popup { font-size: 13px; line-height: 1.5; color: #334155; }
.map-popup strong { display: block; color: #0f172a; margin-bottom: 2px; }
.leaflet-popup-content-wrapper {
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(10,40,30,0.16) !important;
}
.leaflet-popup-tip-container { display: none !important; }
</style>