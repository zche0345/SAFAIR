<template>
  <div class="assistance-page">

    <!-- ── Intro Modal ──────────────────────────────────────── -->
    <transition name="modal-fade">
      <div v-if="showIntroModal" class="modal-backdrop" @click.self="dismissModal">
        <div class="modal-box" role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <button class="modal-close" @click="dismissModal" aria-label="Close">✕</button>

          <p class="modal-eyebrow">ASSISTANCE</p>
          <h2 id="modal-title">Your three protection tools</h2>
          <p class="modal-desc">
            This page brings together three real-time tools to help you protect your child before
            and during any activity. Switch between them using the slider at the top of the map.
          </p>

          <div class="modal-tools">
            <div class="modal-tool-card">
              <div class="modal-tool-header">
                <span class="tool-dot dustwatch"></span>
                <strong>DustWatch</strong>
                <span class="tool-badge realtime">Real-time</span>
              </div>
              <p>Shows active construction sites near your suburb and their current dust levels. Select a suburb to see a live map and ranked site list.</p>
            </div>

            <div class="modal-tool-card">
              <div class="modal-tool-header">
                <span class="tool-dot safespots"></span>
                <strong>SafeSpots</strong>
                <span class="tool-badge ai">AI-assisted</span>
              </div>
              <p>Finds asthma-safe parks and outdoor spaces near you, scored using live traffic, dust, pollen, and microclimate data. Powered by AI to rank the safest options.</p>
            </div>

            <div class="modal-tool-card">
              <div class="modal-tool-header">
                <span class="tool-dot clearpath"></span>
                <strong>ClearPath</strong>
                <span class="tool-badge ai">AI-assisted</span>
              </div>
              <p>Plans the safest walking or cycling route to your destination, avoiding dust zones, pollen hotspots, and high-traffic roads. AI selects and scores the routes.</p>
            </div>
          </div>

          <div class="modal-safeshelf">
            <p class="modal-safeshelf-eyebrow">ALSO CHECK YOUR HOME</p>
            <p>Outdoor protection is only part of the picture. SafeShelf checks the products in your home for hidden asthma triggers.</p>
            <button class="btn-safeshelf" @click="dismissModal">Open SafeShelf</button>
          </div>

          <button class="btn-show-map" @click="dismissModal">
            Got it — show me the map
          </button>
        </div>
      </div>
    </transition>

    <!-- ── Main Layout: map fills viewport, panel overlaid ─── -->
    <div class="page-layout">

      <!-- Tab switcher — floats above map -->
      <div class="tab-switcher">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id, [tab.id]: true }"
          @click="switchTab(tab.id)"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Location hint -->
      <div class="location-hint">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        Uses your location to show nearby results
      </div>

      <!-- Left floating panel -->
      <aside class="side-panel">

        <!-- ── DUSTWATCH PANEL ─────────────────────────── -->
        <template v-if="activeTab === 'dustwatch'">
          <p class="panel-desc">Real-time dust levels from active construction sites in your suburb. Check before heading out with your child.</p>

          <div v-if="activeArea.riskLevel" class="overall-risk-block">
            <div class="risk-label-row">
              <span class="risk-eyebrow">OVERALL RISK</span>
              <span class="risk-site-count">{{ activeArea.activeSites.length }} active sites</span>
            </div>
            <p class="risk-level-text" :class="activeArea.riskLevel.toLowerCase()">
              {{ activeArea.riskLevel }} Dust
            </p>
          </div>

          <!-- Suburb selector -->
          <div class="suburb-selector-row">
            <button class="suburb-current-btn" @click="showSuburbDropdown = !showSuburbDropdown">
              {{ selectedSuburb }}
            </button>
            <button class="check-suburb-btn" @click="showSuburbDropdown = !showSuburbDropdown">
              Check Another Suburb
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline :points="showSuburbDropdown ? '18 15 12 9 6 15' : '6 9 12 15 18 9'"/></svg>
            </button>
          </div>

          <transition name="dropdown">
            <div v-if="showSuburbDropdown" class="suburb-dropdown">
              <p class="suburb-dropdown-label">SELECT A SUBURB</p>
              <div class="suburb-pills-grid">
                <button
                  v-for="suburb in suburbs"
                  :key="suburb"
                  class="suburb-pill-btn"
                  :class="{ active: suburb === selectedSuburb && !outsideCoverage }"
                  @click="pickSuburb(suburb)"
                >
                  {{ suburb }}
                </button>
              </div>
            </div>
          </transition>

          <!-- Location button -->
          <button
            class="use-location-btn"
            :disabled="!locationEnabled || dustLoading"
            @click="useMyLocation"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>
            {{ dustLoading ? 'Loading…' : 'Use My Location' }}
          </button>

          <!-- Out of coverage -->
          <div v-if="activeArea.inCoverage === false" class="coverage-notice">
            <strong>Outside coverage area</strong>
            <p>Construction dust data is only available for inner Melbourne suburbs.</p>
          </div>

          <!-- Sites list -->
          <template v-else>
            <p v-if="dustError" class="panel-error">{{ dustError }}</p>

            <div v-if="activeArea.activeSites.length" class="sites-label">
              SITES NEAR {{ selectedSuburb.toUpperCase() }}
            </div>

            <div class="sites-scroll-list">
              <article
                v-for="site in activeArea.activeSites"
                :key="site.siteId"
                class="site-row"
                :class="{ selected: selectedSiteId === site.siteId }"
                @click="handleSiteSelect(site)"
              >
                <div class="site-row-info">
                  <strong>{{ site.title }}</strong>
                  <span>{{ site.distance }}</span>
                </div>
                <span class="site-risk-chip" :class="site.riskTone">
                  {{ riskBadgeLabel(site.riskLabel) }}
                </span>
              </article>
            </div>

            <div class="panel-updated">
              <span class="updated-dot"></span>
              Last updated: {{ activeArea.lastUpdated }}
            </div>
          </template>
        </template>

        <!-- ── SAFESPOTS PANEL ─────────────────────────── -->
        <template v-if="activeTab === 'safespots'">
          <p class="panel-desc">Discover asthma-safe parks and outdoor spaces, rated using real-time air quality and dust data.</p>

          <div class="autocomplete-wrap">
            <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <input
              v-model="safeSpotSearch"
              type="text"
              placeholder="Enter suburb or address…"
              class="panel-input has-icon"
              autocomplete="off"
              @input="onSpotInput"
              @keydown.down.prevent="moveSpotActive(1)"
              @keydown.up.prevent="moveSpotActive(-1)"
              @keydown.enter.prevent="pickSpotActive"
              @keydown.escape="spotSuggestions = []"
              @blur="onSpotBlur"
            />
            <transition name="dropdown">
              <ul v-if="spotSuggestions.length" class="suggestions-list">
                <li
                  v-for="(s, i) in spotSuggestions"
                  :key="s.place_id"
                  class="suggestion-item"
                  :class="{ active: i === spotActiveIdx }"
                  @mousedown.prevent="pickSpotSuggestion(i)"
                >
                  <span class="sug-icon-wrap">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C13 21.5 20 15.4 20 10a8 8 0 0 0-8-8z"/></svg>
                  </span>
                  <span class="sug-text">
                    <strong>{{ s._primary }}</strong>
                    <small>{{ s._secondary }}</small>
                  </span>
                </li>
              </ul>
            </transition>
          </div>

          <div class="radius-control">
            <div class="radius-header">
              <span>Search radius</span>
              <span class="radius-value">{{ safeSpotRadius }} <small>km</small></span>
              <button class="radius-info-btn" title="Larger radius finds more spots but may be less accurate">ⓘ</button>
            </div>
            <input
              v-model.number="safeSpotRadius"
              type="range"
              min="1" max="10" step="1"
              class="radius-slider"
            />
            <div class="radius-ticks">
              <span>1km</span><span>3km</span><span>5km</span><span>8km</span><span>10km</span>
            </div>
          </div>

          <button class="btn-find-spots" @click="findSafeSpots" :disabled="safeSpotLoading">
            <span v-if="safeSpotLoading" class="spinner"></span>
            {{ safeSpotLoading ? 'Finding spots…' : 'Find SafeSpots' }}
          </button>

          <transition name="fade">
            <div v-if="safeSpotError" class="panel-error">
              <span>⚠</span> {{ safeSpotError }}
              <button @click="safeSpotError = ''">✕</button>
            </div>
          </transition>

          <!-- Category filters — shown after results load -->
          <div v-if="allSafeSpots.length" class="category-filters">
            <button
              v-for="cat in SPOT_CATEGORIES"
              :key="cat.id"
              class="cat-filter-btn"
              :class="{ active: activeCategory === cat.id }"
              @click="filterByCategory(cat.id)"
            >{{ cat.label }}</button>
          </div>

          <div v-if="safeSpots.length" class="spots-list">
            <article
              v-for="(spot, i) in safeSpots"
              :key="spot.id"
              class="spot-row"
              :class="{ selected: selectedSpotId === spot.id }"
              @click="selectSpot(spot)"
            >
              <div class="spot-rank">{{ i + 1 }}</div>
              <div class="spot-info">
                <strong>{{ spot.name }}</strong>
                <span>{{ spot.suburb }} — {{ spot.distance }}</span>
                <div class="spot-tags">
                  <span
                    v-for="tag in spot.tags.slice(0, 3)"
                    :key="tag"
                    class="spot-tag"
                    :class="tagClass(tag)"
                  >{{ tag }}</span>
                </div>
              </div>
              <div class="spot-score-col">
                <span class="spot-score" :class="scoreClass(spot.score)">{{ spot.score }}</span>
                <button
                  class="spot-clearpath-btn"
                  @click.stop="goToClearPath(spot)"
                >ClearPath</button>
              </div>
            </article>
          </div>

          <p v-else-if="allSafeSpots.length && !safeSpots.length" class="no-filter-results">
            No {{ activeCategory }} spots found. <button @click="filterByCategory('all')">Show all</button>
          </p>
        </template>

        <!-- ── CLEARPATH PANEL ─────────────────────────── -->
        <template v-if="activeTab === 'clearpath'">
          <p class="panel-desc">Find the safest route for your child — avoiding construction dust, pollen, and high-traffic roads.</p>

          <div class="autocomplete-wrap" style="margin-bottom:10px">
            <span class="route-dot start-dot"></span>
            <input
              v-model="startPoint"
              type="text"
              placeholder="Starting point…"
              class="panel-input has-dot"
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
                    <svg v-if="isTransit(s)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
                    <svg v-else-if="isBuilding(s)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
                    <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C13 21.5 20 15.4 20 10a8 8 0 0 0-8-8z"/></svg>
                  </span>
                  <span class="sug-text">
                    <strong>{{ s._primary }}</strong>
                    <small>{{ s._secondary }}</small>
                  </span>
                </li>
              </ul>
            </transition>
          </div>

          <div class="autocomplete-wrap" style="margin-bottom:14px">
            <span class="route-dot end-dot"></span>
            <input
              v-model="destination"
              type="text"
              placeholder="Destination…"
              class="panel-input has-dot"
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
                    <svg v-if="isTransit(s)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
                    <svg v-else-if="isBuilding(s)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
                    <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C13 21.5 20 15.4 20 10a8 8 0 0 0-8-8z"/></svg>
                  </span>
                  <span class="sug-text">
                    <strong>{{ s._primary }}</strong>
                    <small>{{ s._secondary }}</small>
                  </span>
                </li>
              </ul>
            </transition>
          </div>

          <transition name="fade">
            <div v-if="routeError" class="panel-error" role="alert">
              <span>⚠</span> {{ routeError }}
              <button @click="routeError = null">✕</button>
            </div>
          </transition>

          <button
            class="btn-find-routes"
            :disabled="routeLoading"
            @click="findRoutes"
          >
            <span v-if="routeLoading" class="spinner"></span>
            {{ routeLoading ? 'Finding routes…' : 'Find Safe Routes' }}
          </button>

          <!-- Route results -->
          <div v-if="routes.length" class="routes-list">
            <article
              v-for="(route, index) in routes"
              :key="route.name"
              class="route-row"
              :class="[route.tone, { selected: selectedRouteIndex === index }]"
              @click="selectRoute(index)"
            >
              <div class="route-row-top">
                <div class="route-name-wrap">
                  <strong>{{ route.name }}</strong>
                  <span v-if="index === 0" class="best-badge">Best</span>
                </div>
                <span class="route-score-big" :class="route.tone">{{ route.score }}</span>
              </div>
              <div class="route-meta">{{ route.time }} &nbsp;·&nbsp; {{ route.distance }}</div>
              <div class="route-tags">
                <span v-for="note in route.notes.slice(0,2)" :key="note" class="route-tag" :class="route.tone">
                  {{ note.replace('✓ ', '').replace('⚠ ', '') }}
                </span>
              </div>
            </article>
          </div>
        </template>

      </aside>

      <!-- Map container — fills full page -->
      <div ref="mapContainer" class="map-container"></div>

      <!-- Right legend panel -->
      <div class="legend-panel">
        <template v-if="activeTab === 'dustwatch'">
          <div class="legend-item"><span class="legend-dot high"></span><span>High Dust</span></div>
          <div class="legend-item"><span class="legend-dot moderate"></span><span>Moderate</span></div>
          <div class="legend-item"><span class="legend-dot low"></span><span>Low</span></div>
          <div class="legend-item"><span class="legend-dot location"></span><span>Your location</span></div>
        </template>
        <template v-else-if="activeTab === 'safespots'">
          <div class="legend-item"><span class="legend-dot high-risk"></span><span>High risk (75+)</span></div>
          <div class="legend-item"><span class="legend-dot moderate-risk"></span><span>Moderate (25-75)</span></div>
          <div class="legend-item"><span class="legend-dot good"></span><span>Good (0-25)</span></div>
        </template>
        <template v-else>
          <div class="legend-item"><span class="legend-line recommended"></span><span>Recommended</span></div>
          <div class="legend-item"><span class="legend-line alternative"></span><span>Alternative</span></div>
        </template>
      </div>

      <!-- Active alert card (DustWatch only) -->
      <transition name="fade">
        <div v-if="activeTab === 'dustwatch' && activeArea.riskLevel === 'High'" class="alert-card">
          <p class="alert-eyebrow">ACTIVE ALERT</p>
          <strong>High dust in {{ selectedSuburb }}</strong>
          <p>{{ activeArea.activeSites.length }} active sites within 2km reporting elevated dust. Avoid outdoor play 10am - 3pm.</p>
        </div>
      </transition>

      <!-- Disclaimer -->
      <div class="disclaimer-note">
        <strong>Note:</strong> Environmental guidance only. Always follow your child's asthma action plan.
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import {
  requestNotificationPermission,
  subscribeToPush,
  unsubscribeFromPush,
} from '../utils/pushNotifications'

// ── Constants ────────────────────────────────────────────────────
const ROUTE_API_BASE    = 'https://d204zergykc1k6.cloudfront.net/safe-route'
const DUST_API_BASE     =  'https://d204zergykc1k6.cloudfront.net'
const SAFESPOTS_API_BASE = 'https://d204zergykc1k6.cloudfront.net/safe-route'
const USER_ID_KEY    = 'safair_user_id'
const VAPID_PUBLIC_KEY = 'BKQZlKonq6g7x2ocp8Z0z1Ay_CzkI832VCMDSMUbFgdkI9Px56qllIsB5qfZ1lajm7MmUJl6-30pv-ax4kI6f0o'

const FALLBACK_SUBURBS = [
  'Carlton', 'Carlton North', 'Docklands', 'East Melbourne',
  'Fitzroy', 'Flemington', 'Kensington', 'North Melbourne',
  'Parkville', 'Port Melbourne', 'South Wharf', 'Southbank', 'West Melbourne',
]

const SUBURB_COORDS = {
  Carlton:          { lat: -37.8008, lon: 144.9669 },
  'Carlton North':  { lat: -37.7880, lon: 144.9700 },
  Docklands:        { lat: -37.8147, lon: 144.9489 },
  'East Melbourne': { lat: -37.8167, lon: 144.9875 },
  Fitzroy:          { lat: -37.7978, lon: 144.9784 },
  Flemington:       { lat: -37.7881, lon: 144.9285 },
  Kensington:       { lat: -37.7942, lon: 144.9271 },
  Melbourne:        { lat: -37.8136, lon: 144.9631 },
  'North Melbourne':{ lat: -37.7994, lon: 144.9460 },
  Parkville:        { lat: -37.7873, lon: 144.9510 },
  'Port Melbourne': { lat: -37.8335, lon: 144.9397 },
  'South Wharf':    { lat: -37.8270, lon: 144.9526 },
  Southbank:        { lat: -37.8250, lon: 144.9640 },
  'West Melbourne': { lat: -37.8098, lon: 144.9424 },
}

const tabs = [
  { id: 'dustwatch', label: 'DustWatch' },
  { id: 'safespots', label: 'SafeSpots' },
  { id: 'clearpath', label: 'ClearPath' },
]


// ── Global state ─────────────────────────────────────────────────
const showIntroModal = ref(true)
const activeTab      = ref('dustwatch')
const mapContainer   = ref(null)

// ── DustWatch state (ported from ConstructionDustPage) ───────────
const selectedSuburb      = ref('Melbourne')
const suburbs             = ref([...FALLBACK_SUBURBS])
const areaBySuburb        = ref({})
const dustLoading         = ref(false)
const dustError           = ref('')
const locationEnabled     = ref(true)
const pushEnabled         = ref(false)
const selectedSiteId      = ref(null)
const outsideCoverage     = ref(false)
const showSuburbDropdown  = ref(false)
const currentLat          = ref(null)
const currentLon          = ref(null)
const usingPreciseLocation= ref(false)

const fallbackArea = {
  lastUpdated: '--:--',
  summaryEyebrow: 'NEARBY CONSTRUCTION SITES',
  summaryTitle: 'No active construction sites nearby',
  summaryText: 'We could not find active sites near this location right now.',
  riskLevel: null,
  riskRecommendation: '',
  activeSites: [],
  inCoverage: true,
  tips: ['Carry your reliever inhaler when leaving home', 'Choose routes away from visible construction dust when possible', 'Shorten vigorous outdoor sessions if symptoms appear'],
}

const createFallbackSitesForSuburb = (suburbName = 'Melbourne') => {
  const baseCoords = SUBURB_COORDS[suburbName] || SUBURB_COORDS.Melbourne
  return [
    { siteId: `${suburbName}-s1`, title: `123 Main Street, ${suburbName}`,     type: 'Active demolition',      distance: '0.4 km', distanceM: 400,  lat: baseCoords.lat + 0.0022, lon: baseCoords.lon - 0.0018, riskLabel: 'High Risk',     riskTone: 'high' },
    { siteId: `${suburbName}-s2`, title: `45 City Road, ${suburbName}`,        type: 'Foundation excavation',  distance: '0.8 km', distanceM: 800,  lat: baseCoords.lat - 0.0026, lon: baseCoords.lon + 0.0019, riskLabel: 'High Risk',     riskTone: 'high' },
    { siteId: `${suburbName}-s3`, title: `78 Clarendon Street, ${suburbName}`, type: 'Ongoing construction',   distance: '1.1 km', distanceM: 1100, lat: baseCoords.lat + 0.0035, lon: baseCoords.lon + 0.0030, riskLabel: 'Moderate Risk', riskTone: 'moderate' },
    { siteId: `${suburbName}-s4`, title: `12 Park Street, ${suburbName}`,      type: 'Low-impact work',        distance: '1.5 km', distanceM: 1500, lat: baseCoords.lat - 0.0038, lon: baseCoords.lon - 0.0024, riskLabel: 'Low Risk',      riskTone: 'low' },
    { siteId: `${suburbName}-s5`, title: `234 Sturt Street, ${suburbName}`,    type: 'Minimal dust activity',  distance: '1.9 km', distanceM: 1900, lat: baseCoords.lat + 0.0012, lon: baseCoords.lon + 0.0042, riskLabel: 'Low Risk',      riskTone: 'low' },
  ]
}

const createFallbackAreaForSuburb = (suburbName = 'Melbourne') => ({
  lastUpdated: new Date().toLocaleTimeString('en-AU', { hour: 'numeric', minute: '2-digit' }),
  inCoverage: true,
  summaryEyebrow: 'NEARBY CONSTRUCTION SITES',
  summaryTitle: 'At least 5 active construction sites nearby',
  summaryText: `Nearest active permits around ${suburbName} center are shown below.`,
  riskLevel: 'High',
  riskRecommendation: 'Consider choosing quieter streets and avoid long outdoor activity near active works today.',
  activeSites: createFallbackSitesForSuburb(suburbName),
  tips: fallbackArea.tips,
})

const activeArea = computed(() => areaBySuburb.value[selectedSuburb.value] || fallbackArea)

const mapCenter = computed(() => {
  if (usingPreciseLocation.value && typeof currentLat.value === 'number' && typeof currentLon.value === 'number') {
    return { lat: currentLat.value, lon: currentLon.value, label: 'your current location' }
  }
  const c = SUBURB_COORDS[selectedSuburb.value] || SUBURB_COORDS.Melbourne
  return { lat: c.lat, lon: c.lon, label: `${selectedSuburb.value} center` }
})

// ── SafeSpots state (demo) ───────────────────────────────────────
const safeSpotSearch   = ref('')
const safeSpotRadius   = ref(2)
const safeSpotLoading  = ref(false)
const safeSpotError    = ref('')
const safeSpots        = ref([])
const allSafeSpots     = ref([])   // unfiltered full list
const selectedSpotId   = ref(null)
const activeCategory   = ref('all')
const spotSuggestions  = ref([])
const spotActiveIdx    = ref(-1)
let spotTimer = null
const safeSpotOriginLat = ref(null)
const safeSpotOriginLon = ref(null)

const SPOT_CATEGORIES = [
  { id: 'all',        label: 'All' },
  { id: 'park',       label: 'Parks' },
  { id: 'playground', label: 'Playgrounds' },
  { id: 'childcare',  label: 'Childcare' },
  { id: 'landmark',   label: 'Landmarks' },
]

function onSpotInput() {
  clearTimeout(spotTimer)
  const q = safeSpotSearch.value
  if (!q || q.length < 2) { spotSuggestions.value = []; return }
  spotTimer = setTimeout(async () => {
    const results = await fetchSuggestions(q)
    spotSuggestions.value = results
    spotActiveIdx.value = -1
  }, 300)
}

function moveSpotActive(dir) {
  const next = Math.max(-1, Math.min(spotSuggestions.value.length - 1, spotActiveIdx.value + dir))
  spotActiveIdx.value = next
}

function pickSpotActive() {
  if (spotActiveIdx.value >= 0) pickSpotSuggestion(spotActiveIdx.value)
  else findSafeSpots()
}

function pickSpotSuggestion(index) {
  const item = spotSuggestions.value[index]
  if (!item) return
  safeSpotSearch.value = item._secondary ? `${item._primary}, ${item._secondary}` : item._primary
  spotSuggestions.value = []
  spotActiveIdx.value = -1
  findSafeSpots()
}

function onSpotBlur() {
  setTimeout(() => { spotSuggestions.value = [] }, 150)
}

function filterByCategory(cat) {
  activeCategory.value = cat
  if (cat === 'all') {
    safeSpots.value = [...allSafeSpots.value]
  } else {
    safeSpots.value = allSafeSpots.value.filter(s => s.category === cat)
  }
}

// ── ClearPath state (ported from SafeRoutePlanning) ──────────────
const startPoint          = ref('')
const destination         = ref('')
const routeLoading        = ref(false)
const routeError          = ref(null)
const routes              = ref([])
const selectedRouteIndex  = ref(0)
const routeGeometries     = ref([])
const dustZones           = ref([])
const pollenZones         = ref([])
const startSuggestions    = ref([])
const destSuggestions     = ref([])
const startActiveIdx      = ref(-1)
const destActiveIdx       = ref(-1)
let startTimer = null
let destTimer  = null

// ── Leaflet (outside Vue reactivity) ────────────────────────────
let leafletMap     = null
let routeLayers    = []
let zoneLayers     = []
let dustMarkers    = []
let spotMarkers    = []

// ────────────────────────────────────────────────────────────────
// Utilities
// ────────────────────────────────────────────────────────────────
const getUserId = () => {
  let id = localStorage.getItem(USER_ID_KEY)
  if (!id) { id = crypto.randomUUID(); localStorage.setItem(USER_ID_KEY, id) }
  return id
}

const buildDustApiUrl = (path) => `${DUST_API_BASE.replace(/\/$/, '')}${path}`
const buildPreferencesUrl  = () => buildDustApiUrl('/user-preferences-api')
const buildCurrentRiskUrl  = (s) => buildDustApiUrl(`/api/current-risk?suburb=${encodeURIComponent(s)}`)

const riskBadgeLabel = (label = '') => label.replace('Risk', 'Dust')

const tagClass = (tag = '') => {
  const t = tag.toLowerCase()
  if (t.includes('no active') || t.includes('quiet') || t.includes('good') || t.includes('low dust') || t.includes('minimal pollen') || t.includes('outside')) return 'tag-good'
  if (t.includes('moderate') || t.includes('some') || t.includes('warn')) return 'tag-warn'
  if (t.includes('high') || t.includes('busy') || t.includes('heavy')) return 'tag-bad'
  return 'tag-neutral'
}

const scoreClass = (score) => {
  if (score >= 70) return 'score-good'
  if (score >= 40) return 'score-moderate'
  return 'score-poor'
}


// ────────────────────────────────────────────────────────────────
// Modal
// ────────────────────────────────────────────────────────────────
function dismissModal() {
  showIntroModal.value = false
}

// ────────────────────────────────────────────────────────────────
// Tab switching
// ────────────────────────────────────────────────────────────────
async function switchTab(tabId) {
  activeTab.value = tabId
  await nextTick()
  if (tabId === 'dustwatch') renderDustMap()
  else if (tabId === 'safespots') renderSafeSpotsMap()
  else if (tabId === 'clearpath') {
    clearLeafletMap()
    initBaseMap(SUBURB_COORDS.Melbourne.lat, SUBURB_COORDS.Melbourne.lon)
  }
}

// ────────────────────────────────────────────────────────────────
// Leaflet helpers
// ────────────────────────────────────────────────────────────────
function loadLeaflet() {
  return new Promise(resolve => {
    if (window.L) return resolve(window.L)
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    link.crossOrigin = 'anonymous'
    document.head.appendChild(link)
    const script = document.createElement('script')
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
    script.crossOrigin = 'anonymous'
    script.onload = () => resolve(window.L)
    document.head.appendChild(script)
  })
}

function clearLeafletMap() {
  if (!leafletMap) return
  ;[...routeLayers, ...zoneLayers, ...dustMarkers, ...spotMarkers].forEach(l => {
    try { leafletMap.removeLayer(l) } catch {}
  })
  routeLayers = []; zoneLayers = []; dustMarkers = []; spotMarkers = []
}

async function initBaseMap(lat, lon) {
  const L = await loadLeaflet()
  if (!mapContainer.value) return
  if (leafletMap) {
    leafletMap.setView([lat, lon], 14)
    return L
  }
  leafletMap = L.map(mapContainer.value, { zoomControl: true, scrollWheelZoom: false })
    .setView([lat, lon], 14)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OSM</a> © <a href="https://carto.com/">CARTO</a>',
    maxZoom: 19,
  }).addTo(leafletMap)
  return L
}

// ── DustWatch map ────────────────────────────────────────────────
async function renderDustMap() {
  const L = await initBaseMap(mapCenter.value.lat, mapCenter.value.lon)
  if (!L) return
  clearLeafletMap()

  const boundsPoints = []
  const getRiskColor = (tone) => tone === 'high' ? '#ea2951' : tone === 'moderate' ? '#d36c00' : '#11915d'
  const getRiskRadius = (tone) => tone === 'high' ? 80 : tone === 'moderate' ? 60 : 45

  // Centre marker
  const centerMarker = L.circleMarker([mapCenter.value.lat, mapCenter.value.lon], {
    radius: 10, color: '#1d4ed8', fillColor: '#3b82f6', fillOpacity: 0.95, weight: 2,
  }).bindPopup(`<strong>${mapCenter.value.label}</strong>`)
  centerMarker.addTo(leafletMap)
  dustMarkers.push(centerMarker)
  boundsPoints.push([mapCenter.value.lat, mapCenter.value.lon])

  activeArea.value.activeSites.forEach(site => {
    if (typeof site.lat !== 'number' || typeof site.lon !== 'number') return
    const color = getRiskColor(site.riskTone)
    const isSelected = selectedSiteId.value && String(selectedSiteId.value) === String(site.siteId)
    const radius = getRiskRadius(site.riskTone)

    const circle = L.circle([site.lat, site.lon], {
      color, fillColor: color,
      fillOpacity: isSelected ? 0.34 : 0.2,
      radius: isSelected ? radius * 1.9 : radius,
      weight: isSelected ? 4 : 2,
      opacity: isSelected ? 0.95 : 0.8,
    })
    const marker = L.circleMarker([site.lat, site.lon], {
      radius: isSelected ? 13 : 8,
      color: isSelected ? '#ffffff' : color,
      fillColor: color, fillOpacity: 0.98,
      weight: isSelected ? 4 : 2,
    })
    const popup = `<div style="min-width:160px"><strong>${site.title}</strong><br/>${site.type}<br/>${site.distance}<br/><strong>${site.riskLabel}</strong></div>`
    circle.bindPopup(popup)
    marker.bindPopup(popup)
    circle.addTo(leafletMap)
    marker.addTo(leafletMap)
    dustMarkers.push(circle, marker)
    boundsPoints.push([site.lat, site.lon])
  })

  if (boundsPoints.length > 1) {
    leafletMap.fitBounds(boundsPoints, { padding: [40, 40] })
  }
}

// ── SafeSpots map ────────────────────────────────────────────────
async function renderSafeSpotsMap() {
  const centerLat = safeSpotOriginLat.value ?? SUBURB_COORDS.Melbourne.lat
  const centerLon = safeSpotOriginLon.value ?? SUBURB_COORDS.Melbourne.lon
  const L = await initBaseMap(centerLat, centerLon)
  if (!L) return
  clearLeafletMap()

  const getColor = (score) => score >= 70 ? '#11915d' : score >= 40 ? '#d36c00' : '#ea2951'

  safeSpots.value.forEach(spot => {
    const color = getColor(spot.score)
    const isSelected = selectedSpotId.value === spot.id

    const circle = L.circle([spot.lat, spot.lon], {
      color, fillColor: color,
      fillOpacity: isSelected ? 0.3 : 0.15,
      radius: isSelected ? 120 : 80,
      weight: isSelected ? 3 : 2,
    })

    const icon = L.divIcon({
      className: '',
      html: `<div style="width:32px;height:32px;border-radius:50%;background:${color};border:3px solid white;box-shadow:0 4px 12px rgba(0,0,0,0.2);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px;color:white;">${spot.score}</div>`,
      iconAnchor: [16, 16],
    })
    const marker = L.marker([spot.lat, spot.lon], { icon })
    marker.bindPopup(`<div style="min-width:150px"><strong>${spot.name}</strong><br/>${spot.suburb}<br/>Safety score: <strong>${spot.score}</strong></div>`)

    circle.addTo(leafletMap)
    marker.addTo(leafletMap)
    spotMarkers.push(circle, marker)
  })

  if (safeSpots.value.length > 0) {
    const bounds = safeSpots.value.map(s => [s.lat, s.lon])
    leafletMap.fitBounds(bounds, { padding: [60, 60] })
  }
}

// ── Route map ────────────────────────────────────────────────────
const ROUTE_COLOURS = ['#0d9488', '#d97706', '#7c3aed', '#e24d32']

function drawZones() {
  if (!leafletMap) return
  const L = window.L
  zoneLayers.forEach(l => leafletMap.removeLayer(l))
  zoneLayers = []
  dustZones.value.forEach(z => {
    const c = L.circle([z.lat, z.lon], { radius: z.radius, color: '#e45d3e', fillColor: '#e45d3e', fillOpacity: 0.12, weight: 2, dashArray: '5 6' }).addTo(leafletMap)
    c.bindTooltip(`🏗 Dust zone — ${z.label}`, { sticky: true, className: 'zone-tip' })
    zoneLayers.push(c)
  })
  pollenZones.value.forEach(z => {
    const c = L.circle([z.lat, z.lon], { radius: z.radius, color: '#2f8a5e', fillColor: '#2f8a5e', fillOpacity: 0.15, weight: 2, dashArray: '5 6' }).addTo(leafletMap)
    c.bindTooltip('🌿 Pollen zone', { sticky: true, className: 'zone-tip' })
    zoneLayers.push(c)
  })
}

async function drawRoutes(selectedIdx) {
  if (!leafletMap || !routeGeometries.value.length) return
  const L = window.L
  routeLayers.forEach(l => leafletMap.removeLayer(l))
  routeLayers = []

  routeGeometries.value.forEach((geom, idx) => {
    if (idx === selectedIdx || !geom?.coordinates?.length) return
    const ll = geom.coordinates.map(([lon, lat]) => [lat, lon])
    const col = ROUTE_COLOURS[idx] ?? '#888'
    routeLayers.push(L.polyline(ll, { color: col, weight: 3, opacity: 0.45, dashArray: '8 10' }).addTo(leafletMap))
  })

  const sel = routeGeometries.value[selectedIdx]
  if (sel?.coordinates?.length) {
    const ll = sel.coordinates.map(([lon, lat]) => [lat, lon])
    const col = ROUTE_COLOURS[selectedIdx] ?? '#0d9488'
    const glow = L.polyline(ll, { color: col, weight: 16, opacity: 0.08 }).addTo(leafletMap)
    const line = L.polyline(ll, { color: col, weight: 5, opacity: 1, lineJoin: 'round', lineCap: 'round' }).addTo(leafletMap)
    const startIcon = L.divIcon({ className: '', html: `<div style="width:14px;height:14px;border-radius:50%;background:white;border:4px solid ${col};box-shadow:0 4px 12px rgba(10,40,30,.22);"></div>`, iconAnchor: [7, 7] })
    const endIcon   = L.divIcon({ className: '', html: `<div style="width:14px;height:14px;border-radius:3px;background:#2b63bd;border:2.5px solid white;box-shadow:0 4px 12px rgba(10,40,30,.22);transform:rotate(45deg);"></div>`, iconAnchor: [7, 7] })
    const sm = L.marker(ll[0], { icon: startIcon }).addTo(leafletMap).bindPopup(`<div class="map-popup"><strong>Start</strong><br>${startPoint.value}</div>`)
    const em = L.marker(ll[ll.length - 1], { icon: endIcon }).addTo(leafletMap).bindPopup(`<div class="map-popup"><strong>Destination</strong><br>${destination.value}</div>`)
    routeLayers.push(glow, line, sm, em)
    leafletMap.fitBounds(line.getBounds(), { padding: [48, 48] })
  }
}

function selectRoute(index) {
  selectedRouteIndex.value = index
  drawRoutes(index)
}

// ────────────────────────────────────────────────────────────────
// DustWatch logic (ported from ConstructionDustPage)
// ────────────────────────────────────────────────────────────────
const normalizeSuburbName = (v = '') =>
  v.toLowerCase().replace(/\([^)]*\)/g, '').replace(/\b(vic|victoria|melbourne city|city of melbourne)\b/g, '').replace(/[^a-z\s]/g, ' ').replace(/\s+/g, ' ').trim()

const matchSupportedSuburb = (detected = '') => {
  const nd = normalizeSuburbName(detected)
  if (!nd) return 'Melbourne'
  const exact = suburbs.value.find(s => normalizeSuburbName(s) === nd)
  if (exact) return exact
  const partial = suburbs.value.find(s => { const ns = normalizeSuburbName(s); return nd.includes(ns) || ns.includes(nd) })
  return partial || 'Melbourne'
}

const getSuburbFromCoordinates = async (lat, lon) => {
  const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&zoom=16&addressdetails=1`, { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`Reverse geocoding failed (${res.status})`)
  const data = await res.json()
  const a = data?.address || {}
  return a.suburb || a.neighbourhood || a.city_district || a.town || a.city || a.municipality || 'Melbourne'
}

const loadCurrentRiskBySuburb = async (suburbName = 'Melbourne') => {
  try {
    const res = await fetch(buildCurrentRiskUrl(suburbName))
    const data = await res.json()
    if (!res.ok || !data.success) throw new Error(data.error || `Current risk failed (${res.status})`)
    return { level: data?.overall_risk?.level || null, recommendation: data?.overall_risk?.recommendation || '' }
  } catch { return null }
}

const toBlocksText = (distanceM, sourceLabel) => {
  if (!Number.isFinite(distanceM)) return `Distance from ${sourceLabel} unavailable`
  const blocks = Math.max(1, Math.round(distanceM / 100))
  return `${blocks} ${blocks === 1 ? 'block' : 'blocks'} from ${sourceLabel} (${Math.round(distanceM)} m)`
}

const getSiteRiskMeta = (distanceM) => {
  if (Number.isFinite(distanceM) && distanceM <= 250) return { riskLabel: 'High Risk',     riskTone: 'high' }
  if (Number.isFinite(distanceM) && distanceM <= 500) return { riskLabel: 'Moderate Risk', riskTone: 'moderate' }
  return { riskLabel: 'Low Risk', riskTone: 'low' }
}

const getSiteType = (site) => site.workType || site.permitType || site.category || site.description || 'Active construction work'

const mapNearbyPayloadToArea = (payload, suburbName = 'Melbourne', currentRisk = null) => {
  const queryMode  = payload?.queryMode || 'suburb'
  const sourceLabel = queryMode === 'coords' ? 'your current location' : `${suburbName || payload?.selectedSuburb || 'selected suburb'} center`
  const activeSites = (payload?.sites || []).map(site => {
    const distanceM = Number(site.distanceM)
    return { siteId: site.siteId || `${site.address}-${site.distanceM}`, title: site.address || 'Unknown address', type: getSiteType(site), distance: toBlocksText(distanceM, sourceLabel), distanceM, lat: typeof site.lat === 'number' ? site.lat : null, lon: typeof site.lon === 'number' ? site.lon : null, ...getSiteRiskMeta(distanceM) }
  })
  const inCoverage  = payload?.inCoverage !== false
  const hasSites    = activeSites.length > 0
  const resultCount = Number(payload?.count ?? activeSites.length)
  const cappedAtFive= resultCount >= 5
  return {
    lastUpdated: new Date().toLocaleTimeString('en-AU', { hour: 'numeric', minute: '2-digit' }),
    inCoverage,
    summaryEyebrow: 'NEARBY CONSTRUCTION SITES',
    summaryTitle: hasSites ? (cappedAtFive ? 'At least 5 active construction sites nearby' : `${activeSites.length} active construction sites nearby`) : 'No active construction sites nearby',
    summaryText: hasSites ? (queryMode === 'coords' ? 'Nearest active permits around your current location are shown below.' : `Nearest active permits around ${suburbName || 'this area'} center are shown below.`) : `No active permits were found near ${suburbName || 'this area'} within your search radius.`,
    riskLevel: inCoverage ? currentRisk?.level || null : null,
    riskRecommendation: inCoverage ? currentRisk?.recommendation || '' : '',
    activeSites,
    tips: fallbackArea.tips,
  }
}

const loadNearbyByCoords = async (lat, lon, suburbName = 'Melbourne') => {
  dustLoading.value = true
  dustError.value   = ''
  try {
    const nearbyRes = await fetch(buildDustApiUrl(`/v1/construction/nearby?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&radius=800`))
    const data = await nearbyRes.json()
    if (!nearbyRes.ok || !data.ok) throw new Error(data.message || `Nearby sites failed (${nearbyRes.status})`)
    let currentRisk = null
    if (data.inCoverage !== false) currentRisk = await loadCurrentRiskBySuburb(suburbName)
    const mappedArea = mapNearbyPayloadToArea(data, suburbName, currentRisk)
    outsideCoverage.value = mappedArea.inCoverage === false
    areaBySuburb.value = { ...areaBySuburb.value, [suburbName]: (mappedArea.inCoverage === false || mappedArea.activeSites.length) ? mappedArea : createFallbackAreaForSuburb(suburbName) }
  } catch (err) {
    dustError.value = err.message || 'Could not load dust risk data right now.'
  } finally {
    dustLoading.value = false
  }
}

const loadNearbyBySuburb = async (suburbName = 'Melbourne') => {
  dustLoading.value = true
  dustError.value   = ''
  try {
    const [nearbyRes, currentRisk] = await Promise.all([
      fetch(buildDustApiUrl(`/v1/construction/nearby?suburb=${encodeURIComponent(suburbName)}&radius=800`)),
      loadCurrentRiskBySuburb(suburbName),
    ])
    const data = await nearbyRes.json()
    if (!nearbyRes.ok || !data.ok) throw new Error(data.message || `Nearby sites failed (${nearbyRes.status})`)
    const mappedArea = mapNearbyPayloadToArea(data, suburbName, currentRisk)
    areaBySuburb.value = { ...areaBySuburb.value, [suburbName]: (mappedArea.inCoverage === false || mappedArea.activeSites.length) ? mappedArea : createFallbackAreaForSuburb(suburbName) }
  } catch {
    areaBySuburb.value = { ...areaBySuburb.value, [suburbName]: createFallbackAreaForSuburb(suburbName) }
    dustError.value = ''
  } finally {
    dustLoading.value = false
  }
}

const savePreferences = async (pushSubscription = undefined) => {
  try {
    const body = { locationEnabled: locationEnabled.value, selectedSuburb: selectedSuburb.value, pushEnabled: pushEnabled.value }
    if (pushSubscription !== undefined) body.pushSubscription = pushSubscription
    await fetch(buildPreferencesUrl(), { method: 'PATCH', headers: { 'Content-Type': 'application/json', 'X-Anonymous-User-Id': getUserId() }, body: JSON.stringify(body) })
  } catch (err) { console.error('Failed to save preferences', err) }
}

const loadPreferences = async () => {
  try {
    const res  = await fetch(buildPreferencesUrl(), { headers: { 'X-Anonymous-User-Id': getUserId() } })
    const data = await res.json()
    if (data.ok && data.preferences) {
      locationEnabled.value = typeof data.preferences.locationEnabled === 'boolean' ? data.preferences.locationEnabled : true
      selectedSuburb.value  = typeof data.preferences.selectedSuburb  === 'string'  && data.preferences.selectedSuburb.trim() ? data.preferences.selectedSuburb.trim() : 'Melbourne'
      pushEnabled.value     = typeof data.preferences.pushEnabled     === 'boolean' ? data.preferences.pushEnabled : false
    }
  } catch (err) { console.error('Failed to load preferences', err) }
}

const selectSuburb = async (suburb) => {
  selectedSiteId.value       = null
  usingPreciseLocation.value = false
  currentLat.value           = null
  currentLon.value           = null
  outsideCoverage.value      = false
  selectedSuburb.value       = suburb
  await savePreferences()
  const cachedArea = areaBySuburb.value[suburb]
  if (cachedArea && cachedArea.lastUpdated !== '--:--') return
  await loadNearbyBySuburb(suburb)
}

const pickSuburb = async (suburb) => {
  showSuburbDropdown.value = false
  await selectSuburb(suburb)
  await nextTick()
  if (activeTab.value === 'dustwatch') renderDustMap()
}

const handleSiteSelect = async (site) => {
  selectedSiteId.value = null
  await nextTick()
  selectedSiteId.value = site.siteId
  // Fly to the site — same animation as SafeSpots
  if (leafletMap && typeof site.lat === 'number' && typeof site.lon === 'number') {
    leafletMap.flyTo([site.lat, site.lon], Math.max(leafletMap.getZoom(), 16), {
      duration: 0.7,
      easeLinearity: 0.25,
    })
  }
}

const useMyLocation = async () => {
  if (!locationEnabled.value || !navigator.geolocation) return
  dustLoading.value = true
  dustError.value   = ''
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { latitude, longitude } = position.coords
        currentLat.value = latitude
        currentLon.value = longitude
        usingPreciseLocation.value = true
        const detected = await getSuburbFromCoordinates(latitude, longitude)
        const matched  = matchSupportedSuburb(detected)
        selectedSuburb.value = matched
        await loadNearbyByCoords(latitude, longitude, matched)
        await savePreferences()
        if (activeTab.value === 'dustwatch') renderDustMap()
      } catch {
        await loadNearbyByCoords(position.coords.latitude, position.coords.longitude, selectedSuburb.value)
        await savePreferences()
        dustError.value = 'We found your location, but could not match it to a supported suburb automatically.'
      }
    },
    () => { dustLoading.value = false; dustError.value = 'Location access failed. Showing suburb-based estimates instead.' },
    { enableHighAccuracy: true, timeout: 12000 }
  )
}

// ────────────────────────────────────────────────────────────────
// SafeSpots logic (real API)
// ────────────────────────────────────────────────────────────────
async function findSafeSpots() {
  const query = safeSpotSearch.value.trim()
  if (!query) {
    safeSpotError.value = 'Enter a suburb or address first.'
    return
  }
  safeSpotLoading.value = true
  safeSpotError.value   = ''
  selectedSpotId.value  = null
  safeSpots.value       = []

  try {
    const radiusM = safeSpotRadius.value * 1000
    const url = `${SAFESPOTS_API_BASE}/api/safespots/by-address?q=${encodeURIComponent(query)}&radius=${radiusM}&sort=score&limit=20`
    const res  = await fetch(url)
    const data = await res.json()

    if (!data.success) throw new Error(data.error || 'Could not load SafeSpots.')

    // Normalise API response into the shape the map + list expect
    const mapped = (data.places || []).map(p => ({
      id:       p.id,
      name:     p.name,
      suburb:   p.address || p.category_label || '',
      distance: p.distance_m >= 1000
        ? `${(p.distance_m / 1000).toFixed(1)} km`
        : `${Math.round(p.distance_m)} m`,
      score:    p.safety_score,
      verdict:  p.verdict,
      tags:     (p.highlights || []).map(h => typeof h === 'object' ? h.text : h),
      category: p.category || 'landmark',
      lat:      p.lat,
      lon:      p.lon,
    }))

    allSafeSpots.value = mapped
    activeCategory.value = 'all'
    safeSpots.value = mapped
    // Store origin for map centering
    if (data.origin?.lat && data.origin?.lon) {
      safeSpotOriginLat.value = data.origin.lat
      safeSpotOriginLon.value = data.origin.lon
    }

    if (!safeSpots.value.length) {
      safeSpotError.value = `No safe spots found within ${safeSpotRadius.value} km of "${query}". Try a larger radius.`
    }

    await nextTick()
    renderSafeSpotsMap()

  } catch (err) {
    safeSpotError.value = err.message || 'Could not load SafeSpots right now.'
  } finally {
    safeSpotLoading.value = false
  }
}

function selectSpot(spot) {
  selectedSpotId.value = spot.id
  // Just fly to the spot — no full map re-render
  if (leafletMap && typeof spot.lat === 'number' && typeof spot.lon === 'number') {
    leafletMap.flyTo([spot.lat, spot.lon], Math.max(leafletMap.getZoom(), 16), {
      duration: 0.7,
      easeLinearity: 0.25,
    })
  }
}

function goToClearPath(spot) {
  destination.value = spot.suburb ? `${spot.name}, ${spot.suburb}` : spot.name
  activeTab.value   = 'clearpath'
  nextTick(() => initBaseMap(spot.lat, spot.lon))
}

// ────────────────────────────────────────────────────────────────
// ClearPath logic (ported from SafeRoutePlanning)
// ────────────────────────────────────────────────────────────────
async function fetchSuggestions(query) {
  if (!query || query.length < 2) return []
  try {
    const url = new URL(`${ROUTE_API_BASE}/api/geocode`)
    url.searchParams.set('q', query)
    const res  = await fetch(url.toString())
    const data = await res.json()
    if (!Array.isArray(data)) return []
    return data.map(r => {
      const a = r.address || {}
      const primary = a.amenity || a.building || a.shop || a.tourism || a.leisure || a.office || a.stadium || (a.house_number && a.road ? `${a.house_number} ${a.road}` : null) || a.road || a.suburb || a.city_district || r.display_name.split(',')[0]
      const suburb  = a.suburb || a.city_district || a.neighbourhood || ''
      const state   = a.state_district || a.state || ''
      const postcode= a.postcode || ''
      const secondary = [suburb, state, postcode].filter(Boolean).join(', ')
      return { ...r, _primary: primary, _secondary: secondary }
    })
  } catch { return [] }
}

function isTransit(s) { const t = s.type || ''; const c = s.class || ''; return ['station', 'stop', 'tram_stop', 'bus_stop', 'subway'].includes(t) || c === 'railway' || c === 'public_transport' }
function isBuilding(s) { const t = s.type || ''; const c = s.class || ''; return ['university', 'school', 'hospital', 'hotel', 'restaurant', 'cafe', 'shop', 'building', 'amenity'].includes(t) || c === 'amenity' || c === 'building' || c === 'tourism' }

function onInput(field) {
  const isStart = field === 'start'
  const query   = isStart ? startPoint.value : destination.value
  clearTimeout(isStart ? startTimer : destTimer)
  if (!query || query.length < 2) { isStart ? (startSuggestions.value = []) : (destSuggestions.value = []); return }
  const t = setTimeout(async () => {
    const results = await fetchSuggestions(query)
    if (isStart) { startSuggestions.value = results; startActiveIdx.value = -1 }
    else         { destSuggestions.value  = results; destActiveIdx.value  = -1 }
  }, 300)
  isStart ? (startTimer = t) : (destTimer = t)
}

function moveActive(field, dir) {
  const isStart = field === 'start'
  const list    = isStart ? startSuggestions.value : destSuggestions.value
  const cur     = isStart ? startActiveIdx.value   : destActiveIdx.value
  const next    = Math.max(-1, Math.min(list.length - 1, cur + dir))
  isStart ? (startActiveIdx.value = next) : (destActiveIdx.value = next)
}

function pickActive(field) { const idx = field === 'start' ? startActiveIdx.value : destActiveIdx.value; if (idx >= 0) pickSuggestion(field, idx) }

function pickSuggestion(field, index) {
  const isStart = field === 'start'
  const item    = (isStart ? startSuggestions.value : destSuggestions.value)[index]
  if (!item) return
  const name = item._secondary ? `${item._primary}, ${item._secondary}` : item._primary
  if (isStart) { startPoint.value = name;   startSuggestions.value = []; startActiveIdx.value = -1 }
  else         { destination.value = name;  destSuggestions.value  = []; destActiveIdx.value  = -1 }
}

function clearSuggestions(field) {
  if (field === 'start') { startSuggestions.value = []; startActiveIdx.value = -1 }
  else                   { destSuggestions.value  = []; destActiveIdx.value  = -1 }
}

function onBlur(field) { setTimeout(() => clearSuggestions(field), 150) }

async function geocode(address) {
  try {
    const url = new URL(`${ROUTE_API_BASE}/api/geocode`)
    url.searchParams.set('q', address)
    const res  = await fetch(url.toString())
    const data = await res.json()
    if (Array.isArray(data) && data.length > 0) return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) }
  } catch {}
  return null
}

function scoreToTone(score) { return score <= 35 ? 'best' : score <= 65 ? 'moderate' : 'avoid' }

function shapeRoute(raw, index, isRec) {
  const tone = isRec ? 'best' : scoreToTone(raw.composite_score ?? 50)
  const safetyDisplay = raw.safety_score != null ? `${Math.round(raw.safety_score * 10) / 10}/10` : `${Math.round(100 - (raw.composite_score ?? 50))}/100`
  const notes = []
  if (raw.scores?.raw_dust   != null) notes.push(raw.scores.raw_dust   < 30 ? '✓ Low dust exposure'   : '⚠ Elevated dust along route')
  if (raw.scores?.raw_pollen != null) notes.push(raw.scores.raw_pollen < 30 ? '✓ Low pollen exposure' : '⚠ Elevated pollen along route')
  if (isRec) notes.unshift('✓ Recommended by BRTHEZ')
  return {
    name: ['Route A', 'Route B', 'Route C', 'Route D'][index] ?? `Route ${index + 1}`,
    tag:  { best: 'Best', moderate: 'Moderate', avoid: 'Avoid' }[tone] ?? 'Moderate',
    tone, time: `${Math.round(raw.duration_min ?? 0)} min`,
    distance: raw.distance_m >= 1000 ? `${(raw.distance_m / 1000).toFixed(1)} km` : `${Math.round(raw.distance_m ?? 0)} m`,
    score: safetyDisplay, notes,
  }
}

function buildZones(allRaw, metadata) {
  const dust = []; const pollen = []
  const allCoords = allRaw.flatMap(r => (r?.geometry?.coordinates ?? []).map(([lon, lat]) => ({ lat, lon })))
  if (!allCoords.length) return { dust, pollen }
  const lats = allCoords.map(c => c.lat); const lons = allCoords.map(c => c.lon)
  const minLat = Math.min(...lats) - 0.015; const maxLat = Math.max(...lats) + 0.015
  const minLon = Math.min(...lons) - 0.015; const maxLon = Math.max(...lons) + 0.015
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

async function findRoutes() {
  routeError.value = null
  routeLoading.value = true
  try {
    const [sc, ec] = await Promise.all([geocode(startPoint.value), geocode(destination.value)])
    if (!sc) throw new Error(`Could not locate "${startPoint.value}". Try a more specific address.`)
    if (!ec) throw new Error(`Could not locate "${destination.value}". Try a more specific address.`)

    const params = new URLSearchParams({ start_lat: sc.lat, start_lon: sc.lon, end_lat: ec.lat, end_lon: ec.lon, profile: 'walking', w_dist: 0.333, w_dust: 0.334, w_pollen: 0.333 })
    const res  = await fetch(`${ROUTE_API_BASE}/api/route-compare?${params}`)
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error ?? `API error ${res.status}`)
    const data = await res.json()
    if (!data.success) throw new Error(data.error ?? 'Unknown error')

    const allRaw = [data.recommended]
    if (data.comparison && !data.comparison.is_same_route && data.shortest) allRaw.push(data.shortest)

    routeGeometries.value = allRaw.filter(r => r?.geometry?.coordinates?.length).map(r => r.geometry)
    routes.value          = allRaw.map((r, i) => shapeRoute(r, i, i === 0))
    selectedRouteIndex.value = 0

    const zones = buildZones(allRaw, data.metadata)
    dustZones.value   = zones.dust
    pollenZones.value = zones.pollen

    const coords = routeGeometries.value[0]?.coordinates ?? []
    const mid    = coords[Math.floor(coords.length / 2)]
    await initBaseMap(mid ? mid[1] : sc.lat, mid ? mid[0] : sc.lon)
    drawZones()
    await drawRoutes(0)
  } catch (err) {
    routeError.value = err.message ?? 'Something went wrong. Please try again.'
  } finally {
    routeLoading.value = false
  }
}

// ────────────────────────────────────────────────────────────────
// Lifecycle
// ────────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadPreferences()
  await selectSuburb(selectedSuburb.value)
  await nextTick()
  renderDustMap()
})

onUnmounted(() => {
  if (leafletMap) { leafletMap.remove(); leafletMap = null }
})
</script>

<style scoped>
/* ── Page shell ─────────────────────────────────────────────── */
.assistance-page {
  position: relative;
  width: 100%;
  /* Fill the space below the navbar regardless of how the router mounts this */
  height: calc(100vh - var(--navbar-height, 80px));
  min-height: 500px;
  overflow: hidden;
  background: var(--bg-page, #f5f4f0);
}

.page-layout {
  position: relative;
  width: 100%;
  height: 100%;
}

/* ── Map fills the entire viewport ──────────────────────────── */
.map-container {
  position: absolute;
  inset: 0;
  z-index: 0;
}

/* ── Tab switcher ────────────────────────────────────────────── */
.tab-switcher {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  background: white;
  border-radius: 999px;
  padding: 4px;
  box-shadow: 0 2px 12px rgba(10,40,30,0.1), 0 0 0 1px rgba(10,40,30,0.06);
  gap: 2px;
}

.tab-btn {
  padding: 8px 20px;
  border-radius: 999px;
  border: none;
  background: transparent;
  font-size: 13.5px;
  font-weight: 600;
  color: #6b7a90;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
  white-space: nowrap;
  letter-spacing: 0.01em;
}
.tab-btn:hover { color: var(--text-dark, #0f172a); background: #f5f4f0; }
.tab-btn.active.dustwatch { background: #d97706; color: white; }
.tab-btn.active.safespots { background: #1d4ed8; color: white; }
.tab-btn.active.clearpath { background: var(--primary, #0d6b5e); color: white; }

/* ── Location hint ──────────────────────────────────────────── */
.location-hint {
  position: absolute;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(8px);
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid rgba(10,40,30,0.08);
  box-shadow: 0 2px 8px rgba(10,40,30,0.08);
  white-space: nowrap;
}

/* ── Left side panel ────────────────────────────────────────── */
.side-panel {
  position: absolute;
  top: 96px;
  left: 20px;
  /* Explicit height so it never relies on bottom: 20px alone */
  height: calc(100% - 96px - 20px);
  width: 380px;
  z-index: 10;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 40px rgba(10,40,30,0.14);
  padding: 20px 20px 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scrollbar-width: thin;
  scrollbar-color: rgba(10,40,30,0.1) transparent;
}

.side-panel::-webkit-scrollbar { width: 4px; }
.side-panel::-webkit-scrollbar-thumb { background: rgba(10,40,30,0.12); border-radius: 999px; }

.panel-desc {
  font-size: 13px;
  color: #6b7a90;
  line-height: 1.6;
  margin: 0;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(10,40,30,0.06);
}

/* ── DustWatch panel ────────────────────────────────────────── */
.overall-risk-block {
  background: #fdf8f2;
  border-radius: 14px;
  padding: 16px 18px;
  border: 1px solid rgba(217,119,6,0.12);
}

.risk-label-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}

.risk-eyebrow {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #d97706;
  text-transform: uppercase;
}

.risk-site-count {
  font-size: 13px;
  font-weight: 600;
  color: #8a9ab0;
  line-height: 1;
}
.risk-site-count small { display: none; }

.risk-level-text {
  font-size: 22px;
  font-weight: 800;
  margin: 0;
  line-height: 1;
  letter-spacing: -0.02em;
}
.risk-level-text.high     { color: #ea2951; }
.risk-level-text.moderate { color: #d97706; }
.risk-level-text.low      { color: #11915d; }

/* ── Suburb selector ─────────────────────────────────────────── */
.suburb-selector-row {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.suburb-current-btn {
  background: #d97706;
  color: white;
  border: none;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.suburb-current-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(217,119,6,0.3); }

.check-suburb-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: white;
  border: 1.5px solid rgba(10,40,30,0.12);
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #5a6b7a;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease;
}
.check-suburb-btn:hover { border-color: #d97706; color: #d97706; }

.suburb-dropdown {
  background: white;
  border: 1px solid rgba(10,40,30,0.1);
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 8px 32px rgba(10,40,30,0.1);
}

.suburb-dropdown-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #8a9ab0;
  margin: 0 0 10px;
}

.suburb-pills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.suburb-pill-btn {
  background: #f5f4f0;
  border: 1.5px solid transparent;
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #3d4a63;
  cursor: pointer;
  transition: all 0.2s ease;
}
.suburb-pill-btn:hover  { background: #fdf8f2; border-color: #d97706; color: #d97706; }
.suburb-pill-btn.active { background: #fef3c7; border-color: #d97706; color: #92400e; }

.use-location-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  background: white;
  border: 1.5px solid rgba(10,40,30,0.12);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #3d4a63;
  cursor: pointer;
  width: fit-content;
  transition: border-color 0.2s, color 0.2s;
}
.use-location-btn:hover:not(:disabled) { border-color: #1d4ed8; color: #1d4ed8; }
.use-location-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.coverage-notice {
  background: #fafafa;
  border: 1px solid rgba(10,40,30,0.08);
  border-radius: 12px;
  padding: 14px;
  font-size: 13px;
  color: #5a6b7a;
}
.coverage-notice strong { display: block; color: var(--text-dark); margin-bottom: 4px; }

.sites-label {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #a0aaba;
  margin-top: 2px;
  padding-bottom: 2px;
}

.sites-scroll-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.site-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: #fafafa;
  border: 1.5px solid transparent;
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}
.site-row:hover    { background: white; border-color: rgba(10,40,30,0.09); transform: translateX(3px); box-shadow: 0 2px 12px rgba(10,40,30,0.06); }
.site-row.selected { background: white; border-color: #ea2951; box-shadow: 0 4px 16px rgba(234,41,81,0.1); transform: translateX(3px); }

.site-row-info { min-width: 0; flex: 1; display: flex; flex-direction: column; gap: 3px; }
.site-row-info strong {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-dark, #0f172a);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}
.site-row-info span {
  font-size: 11px;
  color: #9aabb8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.site-risk-chip {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
  flex-shrink: 0;
  letter-spacing: 0.01em;
}
.site-risk-chip.high     { background: #fff0f3; color: #ea2951; }
.site-risk-chip.moderate { background: #fef3c7; color: #d97706; }
.site-risk-chip.low      { background: #ecfdf5; color: #11915d; }

.panel-updated {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  color: #a0aaba;
  padding-top: 8px;
  border-top: 1px solid rgba(10,40,30,0.05);
  margin-top: auto;
}
.updated-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #11915d;
  box-shadow: 0 0 0 3px rgba(17,145,93,0.2);
  flex-shrink: 0;
}

/* ── SafeSpots panel ─────────────────────────────────────────── */
.panel-input {
  width: 100%;
  box-sizing: border-box;
  border: 1.5px solid rgba(10,40,30,0.1);
  background: #f7f4f0;
  border-radius: 12px;
  padding: 12px 14px;
  font: inherit;
  font-size: 14px;
  color: var(--text-dark);
  outline: none;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.panel-input:focus { background: white; border-color: rgba(13,107,94,0.3); box-shadow: 0 0 0 3px rgba(13,148,136,0.1); }
.panel-input::placeholder { color: #9aabb8; }
.panel-input.has-icon { padding-left: 38px; }
.panel-input.has-dot  { padding-left: 36px; }

.autocomplete-wrap { position: relative; }
.input-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #9aabb8; pointer-events: none; }
.route-dot { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); width: 9px; height: 9px; border-radius: 50%; }
.start-dot { background: #0d9488; }
.end-dot   { background: #2b63bd; border-radius: 2px; }

.suggestions-list {
  position: absolute;
  top: calc(100% + 6px);
  left: 0; right: 0;
  background: white;
  border: 1px solid rgba(10,40,30,0.1);
  border-radius: 12px;
  box-shadow: 0 16px 48px rgba(10,40,30,0.14);
  list-style: none;
  margin: 0;
  padding: 5px;
  z-index: 9999;
  max-height: 220px;
  overflow-y: auto;
}
.suggestion-item { display: flex; align-items: center; gap: 10px; padding: 7px 9px; border-radius: 8px; cursor: pointer; transition: background 0.14s; }
.suggestion-item:hover, .suggestion-item.active { background: #e6f7f5; }
.sug-icon-wrap { width: 28px; height: 28px; border-radius: 50%; background: #f0f4f8; flex-shrink: 0; display: flex; align-items: center; justify-content: center; color: #546e8a; }
.suggestion-item.active .sug-icon-wrap, .suggestion-item:hover .sug-icon-wrap { background: #e6f7f5; color: #0d6b5e; }
.sug-text { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.sug-text strong { font-size: 13px; font-weight: 600; color: var(--text-dark); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sug-text small  { font-size: 11px; color: #8a9ab0; }

.radius-control { display: flex; flex-direction: column; gap: 8px; }
.radius-header { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #3d4a63; }
.radius-value { margin-left: auto; font-size: 18px; font-weight: 800; color: #1d4ed8; }
.radius-value small { font-size: 12px; font-weight: 500; color: #8a9ab0; }
.radius-info-btn { background: none; border: none; cursor: pointer; color: #9aabb8; font-size: 14px; }

.radius-slider {
  width: 100%;
  -webkit-appearance: none;
  height: 4px;
  border-radius: 999px;
  background: linear-gradient(to right, #1d4ed8 0%, #1d4ed8 calc((var(--v, 50) - 5) / 15 * 100%), #e2e8f0 calc((var(--v, 50) - 5) / 15 * 100%), #e2e8f0 100%);
  outline: none;
}
.radius-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: #1d4ed8; border: 3px solid white; box-shadow: 0 2px 8px rgba(29,78,216,0.3); cursor: pointer; }

.radius-ticks { display: flex; justify-content: space-between; font-size: 11px; color: #9aabb8; padding: 0 2px; }

.btn-find-spots {
  width: 100%;
  padding: 13px;
  background: #1d4ed8;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.22s ease, box-shadow 0.22s ease, opacity 0.2s;
}
.btn-find-spots:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(29,78,216,0.3); }
.btn-find-spots:disabled { opacity: 0.65; cursor: not-allowed; }

.category-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-bottom: 4px;
}

.cat-filter-btn {
  border: 1.5px solid rgba(10,40,30,0.1);
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #5a6b7a;
  background: white;
  cursor: pointer;
  transition: all 0.18s ease;
}
.cat-filter-btn:hover { border-color: #1d4ed8; color: #1d4ed8; }
.cat-filter-btn.active { background: #1d4ed8; color: white; border-color: #1d4ed8; }

.no-filter-results {
  font-size: 13px;
  color: #8a9ab0;
  text-align: center;
  padding: 12px 0;
}
.no-filter-results button {
  background: none;
  border: none;
  color: #1d4ed8;
  font-weight: 600;
  cursor: pointer;
  font-size: 13px;
}

.spots-list { display: flex; flex-direction: column; gap: 6px; }
.spot-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fafafa;
  border: 1.5px solid transparent;
  border-radius: 12px;
  padding: 11px 12px;
  cursor: pointer;
  transition: all 0.22s ease;
}
.spot-row:hover   { background: white; border-color: rgba(10,40,30,0.1); }
.spot-row.selected{ background: white; border-color: #1d4ed8; box-shadow: 0 4px 16px rgba(29,78,216,0.1); }

.spot-rank { width: 22px; height: 22px; border-radius: 50%; background: #f0f4f8; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; color: #5a6b7a; flex-shrink: 0; margin-top: 1px; }
.spot-info { flex: 1; min-width: 0; }
.spot-info strong { display: block; font-size: 13px; font-weight: 700; color: var(--text-dark); }
.spot-info span   { font-size: 11px; color: #8a9ab0; }
.spot-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.spot-tag  { border-radius: 999px; padding: 3px 9px; font-size: 11px; font-weight: 600; line-height: 1.4; }
.spot-tag.tag-good    { background: #ecfdf5; color: #0d6b5e; }
.spot-tag.tag-warn    { background: #fef3c7; color: #92400e; }
.spot-tag.tag-bad     { background: #fff0f3; color: #be123c; }
.spot-tag.tag-neutral { background: #f0f4f8; color: #546e8a; }

.spot-score-col { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.spot-score { font-size: 20px; font-weight: 800; line-height: 1; }
.spot-score.score-good     { color: #11915d; }
.spot-score.score-moderate { color: #d97706; }
.spot-score.score-poor     { color: #ea2951; }

.spot-clearpath-btn {
  background: #1d4ed8;
  color: white;
  border: none;
  border-radius: 7px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.spot-clearpath-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(29,78,216,0.3); }

/* ── ClearPath panel ─────────────────────────────────────────── */
.btn-find-routes {
  width: 100%;
  padding: 13px;
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.22s ease, box-shadow 0.22s ease, opacity 0.2s;
}
.btn-find-routes:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(13,107,94,0.3); }
.btn-find-routes:disabled { opacity: 0.65; cursor: not-allowed; }

.routes-list { display: flex; flex-direction: column; gap: 8px; }
.route-row {
  background: #fafafa;
  border: 1.5px solid transparent;
  border-radius: 14px;
  padding: 13px 14px;
  cursor: pointer;
  transition: all 0.22s ease;
}
.route-row:hover { background: white; border-color: rgba(10,40,30,0.1); transform: translateX(3px); }
.route-row.selected { background: white; border-color: #0d9488; box-shadow: 0 4px 16px rgba(13,148,136,0.12); }
.route-row.best.selected     { border-color: #0d9488; box-shadow: 0 4px 16px rgba(13,148,136,0.12); }
.route-row.moderate.selected { border-color: #d97706; box-shadow: 0 4px 16px rgba(217,119,6,0.12); }
.route-row.avoid.selected    { border-color: #e24d32; box-shadow: 0 4px 16px rgba(226,77,50,0.12); }

.route-row-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 4px; }
.route-name-wrap { display: flex; align-items: center; gap: 8px; }
.route-name-wrap strong { font-size: 14px; font-weight: 700; color: var(--text-dark); }
.best-badge { background: #ecfdf5; color: #0d6b5e; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 999px; }

.route-score-big { font-size: 18px; font-weight: 800; }
.route-score-big.best     { color: #0d9488; }
.route-score-big.moderate { color: #d97706; }
.route-score-big.avoid    { color: #e24d32; }

.route-meta { font-size: 12px; color: #8a9ab0; margin-bottom: 7px; }
.route-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.route-tag { font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.route-tag.best     { background: #ecfdf5; color: #0d6b5e; }
.route-tag.moderate { background: #fef3c7; color: #92400e; }
.route-tag.avoid    { background: #fff0eb; color: #e24d32; }

/* ── Error / spinner ─────────────────────────────────────────── */
.panel-error {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #fff0eb;
  border: 1.5px solid #e24d32;
  border-radius: 10px;
  padding: 11px 13px;
  font-size: 12px;
  color: #b83215;
  flex: 1;
}
.panel-error button { margin-left: auto; background: none; border: none; cursor: pointer; color: #b83215; flex-shrink: 0; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  display: inline-block;
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ── Right legend panel ──────────────────────────────────────── */
.legend-panel {
  position: absolute;
  top: 96px;
  right: 20px;
  z-index: 10;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(10,40,30,0.08);
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 4px 20px rgba(10,40,30,0.1);
  min-width: 150px;
}

.legend-item { display: flex; align-items: center; gap: 9px; font-size: 13px; font-weight: 600; color: #3d4a63; }
.legend-dot  { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
.legend-dot.high      { background: #ea2951; }
.legend-dot.moderate  { background: #d36c00; }
.legend-dot.low       { background: #11915d; }
.legend-dot.location  { background: #3b82f6; }
.legend-dot.high-risk { background: #ea2951; }
.legend-dot.moderate-risk { background: #d36c00; }
.legend-dot.good      { background: #11915d; }

.legend-line { display: inline-block; width: 20px; height: 3px; border-radius: 999px; flex-shrink: 0; }
.legend-line.recommended { background: #0d9488; }
.legend-line.alternative { background: transparent; border-top: 2.5px dashed #8a9ab0; }

/* ── Alert card ──────────────────────────────────────────────── */
.alert-card {
  position: absolute;
  bottom: 80px;
  right: 20px;
  z-index: 10;
  background: white;
  border: 1px solid rgba(217,119,6,0.2);
  border-radius: 14px;
  padding: 14px 16px;
  max-width: 240px;
  box-shadow: 0 4px 20px rgba(217,119,6,0.12);
}
.alert-eyebrow { font-size: 10px; font-weight: 800; letter-spacing: 0.07em; color: #d97706; margin: 0 0 4px; }
.alert-card strong { display: block; font-size: 14px; color: var(--text-dark); margin-bottom: 4px; }
.alert-card p { margin: 0; font-size: 12px; color: #5a6b7a; line-height: 1.45; }

/* ── Disclaimer ──────────────────────────────────────────────── */
.disclaimer-note {
  position: absolute;
  bottom: 20px;
  right: 20px;
  z-index: 10;
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(10,40,30,0.08);
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 11px;
  color: #5a6b7a;
  max-width: 260px;
}

/* ── Intro modal ─────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(10,20,30,0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-box {
  background: white;
  border-radius: 24px;
  padding: 36px 32px 28px;
  max-width: 520px;
  width: 100%;
  position: relative;
  box-shadow: 0 24px 80px rgba(10,30,20,0.25);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: #f5f4f0;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  color: #5a6b7a;
  transition: background 0.2s;
}
.modal-close:hover { background: #e8e6e0; }

.modal-eyebrow { font-size: 11px; font-weight: 800; letter-spacing: 0.08em; color: var(--primary, #0d6b5e); margin: 0 0 8px; }
.modal-box h2  { font-family: var(--font-serif, Georgia, serif); font-size: 28px; font-weight: 500; color: var(--text-dark, #0f172a); margin: 0 0 10px; }
.modal-desc    { font-size: 14px; color: #5a6b7a; line-height: 1.6; margin: 0 0 22px; }

.modal-tools { display: flex; flex-direction: column; gap: 10px; margin-bottom: 18px; }
.modal-tool-card {
  border: 1.5px solid rgba(10,40,30,0.08);
  border-radius: 14px;
  padding: 14px 16px;
  transition: border-color 0.2s;
}
.modal-tool-card:hover { border-color: rgba(10,40,30,0.16); }
.modal-tool-card p { margin: 0; font-size: 13px; color: #5a6b7a; line-height: 1.5; margin-top: 6px; }

.modal-tool-header { display: flex; align-items: center; gap: 9px; }
.modal-tool-header strong { font-size: 15px; font-weight: 700; color: var(--text-dark); }
.tool-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.tool-dot.dustwatch { background: #d97706; }
.tool-dot.safespots { background: #1d4ed8; }
.tool-dot.clearpath { background: #0d9488; }

.tool-badge { font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 999px; margin-left: auto; }
.tool-badge.realtime { background: #fef3c7; color: #92400e; }
.tool-badge.ai       { background: #ede9fe; color: #5b21b6; }

.modal-safeshelf {
  background: linear-gradient(135deg, #f0fdf8, #e8f9f3);
  border: 1.5px solid rgba(13,148,136,0.2);
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 16px;
}
.modal-safeshelf-eyebrow { font-size: 10px; font-weight: 800; letter-spacing: 0.07em; color: var(--primary, #0d6b5e); margin: 0 0 4px; }
.modal-safeshelf p { font-size: 13px; color: #3d4a63; line-height: 1.5; margin: 0 0 12px; }

.btn-safeshelf {
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 999px;
  padding: 9px 20px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.btn-safeshelf:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(13,107,94,0.3); }

.btn-show-map {
  width: 100%;
  padding: 15px;
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}
.btn-show-map:hover { transform: translateY(-2px); box-shadow: 0 10px 32px rgba(13,107,94,0.32); }

/* ── Transitions ─────────────────────────────────────────────── */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from,   .modal-fade-leave-to     { opacity: 0; }
.modal-fade-enter-active .modal-box,
.modal-fade-leave-active .modal-box { transition: transform 0.3s var(--ease-out-quart, cubic-bezier(0.16,1,0.3,1)); }
.modal-fade-enter-from .modal-box   { transform: translateY(20px) scale(0.97); }
.modal-fade-leave-to   .modal-box   { transform: translateY(10px) scale(0.98); }

.dropdown-enter-active, .dropdown-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.dropdown-enter-from,   .dropdown-leave-to     { opacity: 0; transform: translateY(-6px); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,   .fade-leave-to     { opacity: 0; }

/* ── Responsive ──────────────────────────────────────────────── */
@media (max-width: 960px) {
  .side-panel { position: absolute; width: 100%; top: auto; bottom: 0; left: 0; right: 0; border-radius: 20px 20px 0 0; max-height: 55vh; }
  .legend-panel { display: none; }
  .alert-card   { right: 10px; bottom: calc(55vh + 10px); max-width: 200px; }
  .disclaimer-note { display: none; }
}

@media (max-width: 520px) {
  .tab-btn { padding: 8px 14px; font-size: 13px; }
  .modal-box { padding: 28px 22px 22px; }
  .modal-box h2 { font-size: 24px; }
}
</style>

<!-- Global Leaflet overrides (unscoped) -->
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
.leaflet-popup-content-wrapper { border-radius: 12px !important; box-shadow: 0 8px 32px rgba(10,40,30,0.16) !important; }
.leaflet-popup-tip-container { display: none !important; }
</style>
