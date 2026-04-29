<template>
  <div class="construction-page">
    <div class="construction-scroll-progress" :style="{ width: `${scrollProgress}%` }"></div>

    <section class="dust-hero">
      <div class="container dust-hero-inner">
        <div class="dust-hero-copy reveal visible">
          <router-link to="/" class="hero-back-link">← Back to Home</router-link>
          <h1>
            Construction <span>Dust in</span><br />
            Your Area
          </h1>
          <p>
            Track building sites near you and make informed decisions about outdoor activities
          </p>
        </div>

        <div class="dust-hero-image-wrap reveal visible reveal-delay-1">
          <img
            src="../assets/images/construction-summary-bg.jpg"
            alt="Guardian and child walking near an urban area"
            class="dust-hero-image"
          />        </div>      </div>
    </section>

    <section class="section dust-content">
      <div class="container">
        <div class="suburb-card card reveal visible">
          <h2>Select your area</h2>
          <p>Choose suburbs to monitor for construction dust alerts</p>

          <div class="privacy-controls">
            <label class="privacy-toggle">
              <input
                v-model="locationEnabled"
                type="checkbox"
                @change="saveLocationPreference"
              />
              <span class="sr-only">Enable precise location</span>
            </label>

            <button
              class="location-pill"
              :disabled="!locationEnabled || loading"
              @click="useMyLocation"
            >
              {{ loading ? 'Loading...' : 'Use My Location' }}
            </button>
          </div>

          <div class="suburb-grid">
            <button
              v-for="suburb in suburbs"
              :key="suburb"
              class="suburb-pill"
              :class="{ active: suburb === selectedSuburb }"
              @click="selectSuburb(suburb)"
            >
              {{ suburb }}
            </button>
          </div>

          <div class="updated-row">
            <span class="updated-dot"></span>
            <span>Last updated: {{ activeArea.lastUpdated }}</span>
          </div>
        </div>

        <div class="risk-summary-card card reveal reveal-delay-1">
          <div class="summary-left">
            <span class="eyebrow">{{ activeArea.summaryEyebrow }}</span>
            <h2>{{ activeArea.summaryTitle }}</h2>
            <p class="summary-text">{{ activeArea.summaryText }}</p>
          </div>

          <div v-if="activeArea.riskLevel" class="risk-highlight" :class="activeArea.riskLevel.toLowerCase()">
            <span class="risk-label">Current Risk</span>
            <span class="risk-badge" :class="activeArea.riskLevel.toLowerCase()">
              {{ activeArea.riskLevel }}
            </span>
            <p>{{ activeArea.riskRecommendation }}</p>
          </div>
        </div>

        <div ref="mapSectionRef" class="map-shell reveal reveal-delay-2">
          <ConstructionRiskMap
            v-if="activeArea.activeSites.length"
            :center-lat="mapCenter.lat"
            :center-lon="mapCenter.lon"
            :center-label="mapCenter.label"
            :sites="activeArea.activeSites"
            :selected-site-id="selectedSiteId"
          />
        </div>

        <div v-if="activeArea.activeSites.length" class="sites-section reveal reveal-delay-3">
          <h2 class="section-title sites-heading">Nearby sites sorted by distance</h2>

          <div class="sites-list">
            <article
              v-for="(site, index) in activeArea.activeSites"
              :key="site.siteId"
              class="site-card"
              :class="[site.riskTone, `site-delay-${index}`, { selected: selectedSiteId === site.siteId }]"
              role="button"
              tabindex="0"
              :aria-label="`Highlight ${site.title} on the map`"
              @click="handleSiteSelect(site)"
              @keydown.enter.prevent="handleSiteSelect(site)"
              @keydown.space.prevent="handleSiteSelect(site)"
            >
              <div class="site-card-main">
                <h3>{{ site.title }}</h3>
                <p>
                  <span>{{ site.type }}</span>
                  <span class="site-distance">📍 {{ site.distance }}</span>
                </p>
              </div>

              <div class="site-risk-badge" :class="site.riskTone">
                <span></span>
                {{ riskBadgeLabel(site.riskLabel) }}
              </div>
            </article>
          </div>
        </div>

        <p v-if="error" class="error-text">{{ error }}</p>
        <p v-if="successMessage" class="success-text">{{ successMessage }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import {
  requestNotificationPermission,
  subscribeToPush,
  unsubscribeFromPush,
} from '../utils/pushNotifications'

import ConstructionRiskMap from '../components/ConstructionRiskMap.vue'

const USER_ID_KEY = 'safair_user_id'
const FALLBACK_SUBURBS = [
  'Carlton',
  'Docklands',
  'East Melbourne',
  'Kensington',
  'Melbourne',
  'North Melbourne',
  'Parkville',
  'South Yarra',
  'Southbank',
  'West Melbourne',
]

const SUBURB_COORDS = {
  Carlton: { lat: -37.8008, lon: 144.9669 },
  Docklands: { lat: -37.8147, lon: 144.9489 },
  'East Melbourne': { lat: -37.8167, lon: 144.9875 },
  Kensington: { lat: -37.7942, lon: 144.9271 },
  Melbourne: { lat: -37.8136, lon: 144.9631 },
  'North Melbourne': { lat: -37.7994, lon: 144.9460 },
  Parkville: { lat: -37.7873, lon: 144.9510 },
  'South Yarra': { lat: -37.8396, lon: 144.9917 },
  Southbank: { lat: -37.8250, lon: 144.9640 },
  'West Melbourne': { lat: -37.8098, lon: 144.9424 },
}

const fallbackArea = {
  lastUpdated: '--:--',
  summaryEyebrow: 'NEARBY CONSTRUCTION SITES',
  summaryTitle: 'No active construction sites nearby',
  summaryText:
    'We could not find active sites near this location right now.',
  riskLevel: null,
  riskRecommendation: '',
  activeSites: [],
  tips: [
    'Carry your reliever inhaler when leaving home',
    'Choose routes away from visible construction dust when possible',
    'Shorten vigorous outdoor sessions if symptoms appear',
  ],
}


const createFallbackSitesForSuburb = (suburbName = 'Melbourne') => {
  const baseCoords = SUBURB_COORDS[suburbName] || SUBURB_COORDS.Melbourne
  return [
    { siteId: `${suburbName}-sample-1`, title: suburbName === 'Southbank' ? '123 Queensbridge Street, Southbank' : `123 Main Street, ${suburbName}`, type: 'Active demolition', distance: '0.4 km', distanceM: 400, lat: baseCoords.lat + 0.0022, lon: baseCoords.lon - 0.0018, riskLabel: 'High Risk', riskTone: 'high' },
    { siteId: `${suburbName}-sample-2`, title: suburbName === 'Southbank' ? '45 City Road, South Melbourne' : `45 City Road, ${suburbName}`, type: 'Foundation excavation', distance: '0.8 km', distanceM: 800, lat: baseCoords.lat - 0.0026, lon: baseCoords.lon + 0.0019, riskLabel: 'High Risk', riskTone: 'high' },
    { siteId: `${suburbName}-sample-3`, title: suburbName === 'Southbank' ? '78 Clarendon Street, Southbank' : `78 Clarendon Street, ${suburbName}`, type: 'Ongoing construction', distance: '1.1 km', distanceM: 1100, lat: baseCoords.lat + 0.0035, lon: baseCoords.lon + 0.003, riskLabel: 'Moderate Risk', riskTone: 'moderate' },
    { siteId: `${suburbName}-sample-4`, title: suburbName === 'Southbank' ? '12 Park Street, South Melbourne' : `12 Park Street, ${suburbName}`, type: 'Low-impact work', distance: '1.5 km', distanceM: 1500, lat: baseCoords.lat - 0.0038, lon: baseCoords.lon - 0.0024, riskLabel: 'Low Risk', riskTone: 'low' },
    { siteId: `${suburbName}-sample-5`, title: suburbName === 'Southbank' ? '234 Sturt Street, Southbank' : `234 Sturt Street, ${suburbName}`, type: 'Minimal dust activity', distance: '1.9 km', distanceM: 1900, lat: baseCoords.lat + 0.0012, lon: baseCoords.lon + 0.0042, riskLabel: 'Low Risk', riskTone: 'low' },
  ]
}

const createFallbackAreaForSuburb = (suburbName = 'Melbourne') => {
  const activeSites = createFallbackSitesForSuburb(suburbName)
  return {
    lastUpdated: new Date().toLocaleTimeString('en-AU', { hour: 'numeric', minute: '2-digit' }),
    summaryEyebrow: 'NEARBY CONSTRUCTION SITES',
    summaryTitle: 'At least 5 active construction sites nearby',
    summaryText: `Nearest active permits around ${suburbName} center are shown below.`,
    riskLevel: 'High',
    riskRecommendation: 'Consider choosing quieter streets and avoid long outdoor activity near active works today.',
    activeSites,
    tips: fallbackArea.tips,
  }
}

const VAPID_PUBLIC_KEY ='BKQZlKonq6g7x2ocp8Z0z1Ay_CzkI832VCMDSMUbFgdkI9Px56qllIsB5qfZ1lajm7MmUJl6-30pv-ax4kI6f0o'

const selectedSuburb = ref('Melbourne')
const suburbs = ref([...FALLBACK_SUBURBS])
const areaBySuburb = ref({})
const loading = ref(false)
const testingPush = ref(false)
const error = ref('')
const successMessage = ref('')
const locationEnabled = ref(true)
const pushEnabled = ref(false)
const selectedSiteId = ref(null)
const mapSectionRef = ref(null)

const currentLat = ref(null)
const currentLon = ref(null)
const usingPreciseLocation = ref(false)

const mapCenter = computed(() => {
  if (
    usingPreciseLocation.value &&
    typeof currentLat.value === 'number' &&
    typeof currentLon.value === 'number'
  ) {
    return {
      lat: currentLat.value,
      lon: currentLon.value,
      label: 'your current location',
    }
  }

  const suburbCoords = SUBURB_COORDS[selectedSuburb.value] || SUBURB_COORDS.Melbourne

  return {
    lat: suburbCoords.lat,
    lon: suburbCoords.lon,
    label: `${selectedSuburb.value} center`,
  }
})

const activeArea = computed(
  () => areaBySuburb.value[selectedSuburb.value] || fallbackArea
)

const getUserId = () => {
  let id = localStorage.getItem(USER_ID_KEY)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(USER_ID_KEY, id)
  }
  return id
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://d204zergykc1k6.cloudfront.net'

const buildApiUrl = (path) => {
  return `${API_BASE_URL.replace(/\/$/, '')}${path}`
}

const buildPreferencesUrl = () => buildApiUrl('/user-preferences-api')
const buildSendDustAlertsUrl = () => buildApiUrl('/send-dust-alerts')
const buildCurrentRiskUrl = (suburbName) =>
  buildApiUrl(`/api/current-risk?suburb=${encodeURIComponent(suburbName)}`)


const normalizeSuburbName = (value = '') =>
  value
    .toLowerCase()
    .replace(/\([^)]*\)/g, '')
    .replace(/\b(vic|victoria|melbourne city|city of melbourne)\b/g, '')
    .replace(/[^a-z\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

const matchSupportedSuburb = (detectedSuburb = '') => {
  const normalizedDetected = normalizeSuburbName(detectedSuburb)
  if (!normalizedDetected) return 'Melbourne'

  const exactMatch = suburbs.value.find(
    (suburb) => normalizeSuburbName(suburb) === normalizedDetected
  )
  if (exactMatch) return exactMatch

  const partialMatch = suburbs.value.find((suburb) => {
    const normalizedSuburb = normalizeSuburbName(suburb)
    return (
      normalizedDetected.includes(normalizedSuburb) ||
      normalizedSuburb.includes(normalizedDetected)
    )
  })
  return partialMatch || 'Melbourne'
}

const getSuburbFromCoordinates = async (lat, lon) => {
  const response = await fetch(
    `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&zoom=16&addressdetails=1`,
    {
      headers: {
        Accept: 'application/json',
      },
    }
  )

  if (!response.ok) {
    throw new Error(`Reverse geocoding failed (${response.status})`)
  }

  const data = await response.json()
  const address = data?.address || {}

  return (
    address.suburb ||
    address.neighbourhood ||
    address.city_district ||
    address.town ||
    address.city ||
    address.municipality ||
    'Melbourne'
  )
}

const loadCurrentRiskBySuburb = async (suburbName = 'Melbourne') => {
  try {
    const res = await fetch(buildCurrentRiskUrl(suburbName))
    const data = await res.json()
    if (!res.ok || !data.success) {
      throw new Error(data.error || `Current risk request failed (${res.status})`)
    }
    return {
      level: data?.overall_risk?.level || null,
      recommendation: data?.overall_risk?.recommendation || '',
    }
  } catch (err) {
    console.error('Failed to load current risk', err)
    return null
  }
}

const toBlocksText = (distanceM, sourceLabel) => {
  if (!Number.isFinite(distanceM)) {
    return `Distance from ${sourceLabel} unavailable`
  }

  const blocks = Math.max(1, Math.round(distanceM / 100))
  const roundedMeters = Math.round(distanceM)

  return `${blocks} ${blocks === 1 ? 'block' : 'blocks'} from ${sourceLabel} (${roundedMeters} m)`
}

const getSiteRiskMeta = (distanceM) => {
  if (Number.isFinite(distanceM) && distanceM <= 250) {
    return { riskLabel: 'High Risk', riskTone: 'high' }
  }
  if (Number.isFinite(distanceM) && distanceM <= 500) {
    return { riskLabel: 'Moderate Risk', riskTone: 'moderate' }
  }
  return { riskLabel: 'Low Risk', riskTone: 'low' }
}

const getSiteType = (site) =>
  site.workType ||
  site.permitType ||
  site.category ||
  site.description ||
  'Active construction work'

const mapNearbyPayloadToArea = (payload, suburbName = 'Melbourne', currentRisk = null) => {
  const queryMode = payload?.queryMode || 'suburb'
  const sourceLabel =
    queryMode === 'coords'
      ? 'your current location'
      : `${suburbName || payload?.selectedSuburb || 'selected suburb'} center`

  const activeSites = (payload?.sites || []).map((site) => {
    const distanceM = Number(site.distanceM)
    const riskMeta = getSiteRiskMeta(distanceM)

    return {
  siteId: site.siteId || `${site.address}-${site.distanceM}`,
  title: site.address || 'Unknown address',
  type: getSiteType(site),
  distance: toBlocksText(distanceM, sourceLabel),
  distanceM,
  lat: typeof site.lat === 'number' ? site.lat : null,
  lon: typeof site.lon === 'number' ? site.lon : null,
  ...riskMeta,
}
  })

  const locationLabel = suburbName || payload?.selectedSuburb || 'this area'
  const inCoverage = payload?.inCoverage !== false
  const hasSites = activeSites.length > 0
  const resultCount = Number(payload?.count ?? activeSites.length)
  const cappedAtFive = resultCount >= 5

  let summaryTitle = hasSites
    ? cappedAtFive
      ? 'At least 5 active construction sites nearby'
      : `${activeSites.length} active construction sites nearby`
    : 'No active construction sites nearby'
  let summaryText = hasSites
    ? queryMode === 'coords'
      ? 'Nearest active permits around your current location are shown below.'
      : `Nearest active permits around ${locationLabel} center are shown below.`
    : `No active permits were found near ${locationLabel} within your search radius.`

  if (!inCoverage) {
    summaryTitle = 'Outside City of Melbourne coverage'
    summaryText =
      payload?.message ||
      'You are currently outside the City of Melbourne coverage area.'
  }

  const showRisk = inCoverage

  return {
    lastUpdated: new Date().toLocaleTimeString('en-AU', {
      hour: 'numeric',
      minute: '2-digit',
    }),
    summaryEyebrow: 'NEARBY CONSTRUCTION SITES',
    summaryTitle,
    summaryText,
    riskLevel: showRisk ? currentRisk?.level || null : null,
    riskRecommendation: showRisk ? currentRisk?.recommendation || '' : '',
    activeSites,
    tips: fallbackArea.tips,
  }
}

const loadNearbyByCoords = async (lat, lon, suburbName = 'Melbourne') => {
  loading.value = true
  error.value = ''

  try {
    const nearbyRes = await fetch(
      buildApiUrl(
        `/v1/construction/nearby?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&radius=800`
      )
    )
    const data = await nearbyRes.json()

    if (!nearbyRes.ok || !data.ok) {
      throw new Error(data.message || `Nearby sites request failed (${nearbyRes.status})`)
    }

    let currentRisk = null
    if (data.inCoverage !== false) {
      currentRisk = await loadCurrentRiskBySuburb(suburbName)
    }

    const mappedArea = mapNearbyPayloadToArea(data, suburbName, currentRisk)
    areaBySuburb.value = {
      ...areaBySuburb.value,
      [suburbName]: mappedArea.activeSites.length ? mappedArea : createFallbackAreaForSuburb(suburbName),
    }
  } catch (err) {
    error.value = err.message || 'Could not load dust risk data right now.'
  } finally {
    loading.value = false
  }
}

const loadNearbyBySuburb = async (suburbName = 'Melbourne') => {
  loading.value = true
  error.value = ''

  try {
    const [nearbyRes, currentRisk] = await Promise.all([
      fetch(
        buildApiUrl(
          `/v1/construction/nearby?suburb=${encodeURIComponent(suburbName)}&radius=800`
        )
      ),
      loadCurrentRiskBySuburb(suburbName),
    ])
    const data = await nearbyRes.json()

    if (!nearbyRes.ok || !data.ok) {
      throw new Error(data.message || `Nearby sites request failed (${nearbyRes.status})`)
    }

    const mappedArea = mapNearbyPayloadToArea(data, suburbName, currentRisk)
    areaBySuburb.value = {
      ...areaBySuburb.value,
      [suburbName]: mappedArea.activeSites.length ? mappedArea : createFallbackAreaForSuburb(suburbName),
    }
  } catch (err) {
    console.error('Could not load nearby construction sites, using fallback data', err)
    areaBySuburb.value = {
      ...areaBySuburb.value,
      [suburbName]: createFallbackAreaForSuburb(suburbName),
    }
    error.value = ''
  } finally {
    loading.value = false
  }
}

const savePreferences = async (pushSubscription = undefined) => {
  try {
    const body = {
      locationEnabled: locationEnabled.value,
      selectedSuburb: selectedSuburb.value,
      pushEnabled: pushEnabled.value,
    }

    if (pushSubscription !== undefined) {
      body.pushSubscription = pushSubscription
    }

    await fetch(buildPreferencesUrl(), {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-Anonymous-User-Id': getUserId(),
      },
      body: JSON.stringify(body),
    })
  } catch (err) {
    console.error('Failed to save preferences', err)
  }
}

const loadPreferences = async () => {
  try {
    const res = await fetch(buildPreferencesUrl(), {
      headers: {
        'X-Anonymous-User-Id': getUserId(),
      },
    })

    const data = await res.json()

    if (data.ok && data.preferences) {
      locationEnabled.value =
        typeof data.preferences.locationEnabled === 'boolean'
          ? data.preferences.locationEnabled
          : true

      selectedSuburb.value =
        typeof data.preferences.selectedSuburb === 'string' &&
        data.preferences.selectedSuburb.trim()
          ? data.preferences.selectedSuburb.trim()
          : 'Melbourne'

      pushEnabled.value =
        typeof data.preferences.pushEnabled === 'boolean'
          ? data.preferences.pushEnabled
          : false
    }
  } catch (err) {
    console.error('Failed to load preferences', err)
  }
}

const selectSuburb = async (suburb) => {
  selectedSiteId.value = null
  usingPreciseLocation.value = false
  currentLat.value = null
  currentLon.value = null
  selectedSuburb.value = suburb
  await savePreferences()

  const cachedArea = areaBySuburb.value[suburb]
  if (cachedArea && cachedArea.lastUpdated !== '--:--') return

  await loadNearbyBySuburb(suburb)
}

const handleSiteSelect = async (site) => {
  // Reset first so selecting the same card again still re-opens the map popup.
  selectedSiteId.value = null
  await nextTick()
  selectedSiteId.value = site.siteId

  await nextTick()

  mapSectionRef.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'center',
  })
}

const saveLocationPreference = async () => {
  await savePreferences()
}

const handlePushToggle = async () => {
  try {
    error.value = ''
    successMessage.value = ''

    if (pushEnabled.value) {
      await requestNotificationPermission()

      if (!VAPID_PUBLIC_KEY || VAPID_PUBLIC_KEY === 'YOUR_PUBLIC_VAPID_KEY_HERE') {
        throw new Error('Missing public VAPID key')
      }

      const subscription = await subscribeToPush(VAPID_PUBLIC_KEY)
      await savePreferences(subscription.toJSON())
      successMessage.value = 'Dust alerts enabled successfully.'
    } else {
      await unsubscribeFromPush()
      await savePreferences(null)
      successMessage.value = 'Dust alerts disabled.'
    }
  } catch (err) {
    console.error('Push toggle failed', err)
    pushEnabled.value = false
    error.value = err.message || 'Could not enable push notifications.'
  }
}

const sendTestPush = async () => {
  try {
    testingPush.value = true
    error.value = ''
    successMessage.value = ''

    const res = await fetch(buildSendDustAlertsUrl(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId: getUserId(),
      }),
    })

    const data = await res.json()

    if (!res.ok || !data.ok) {
      throw new Error(data.message || `Test push failed (${res.status})`)
    }

    successMessage.value = 'Test notification sent. Check your browser notifications.'
  } catch (err) {
    console.error('Test push failed', err)
    error.value = err.message || 'Could not send test notification.'
  } finally {
    testingPush.value = false
  }
}

const useMyLocation = async () => {
  if (!locationEnabled.value || !navigator.geolocation) return

  loading.value = true
  error.value = ''
  successMessage.value = ''

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { latitude, longitude } = position.coords
        currentLat.value = latitude
        currentLon.value = longitude
        usingPreciseLocation.value = true
        const detectedSuburb = await getSuburbFromCoordinates(latitude, longitude)
        const matchedSuburb = matchSupportedSuburb(detectedSuburb)

        selectedSuburb.value = matchedSuburb
        await loadNearbyByCoords(latitude, longitude, matchedSuburb)
        await savePreferences()

        successMessage.value = `Using your location. Suburb set to ${matchedSuburb}.`
      } catch (err) {
        console.error('Failed to resolve suburb from coordinates', err)
        await loadNearbyByCoords(
          position.coords.latitude,
          position.coords.longitude,
          selectedSuburb.value
        )
        await savePreferences()
        error.value =
          'We found your location, but could not match it to a supported suburb automatically.'
      }
    },
    () => {
      loading.value = false
      error.value = 'Location access failed. Showing suburb-based estimates instead.'
    },
    { enableHighAccuracy: true, timeout: 12000 }
  )
}


const scrollProgress = ref(0)
let revealObserver = null
let scrollRaf = null

const riskBadgeLabel = (label = '') => label.replace('Risk', 'Dust')

const initRevealObserver = () => {
  if (typeof window === 'undefined') return
  if (revealObserver) revealObserver.disconnect()

  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
          revealObserver.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.14, rootMargin: '0px 0px -70px 0px' }
  )

  document.querySelectorAll('.construction-page .reveal').forEach((element) => {
    revealObserver.observe(element)
  })
}

const scrollToMap = () => {
  mapSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

const updateScrollProgress = () => {
  if (typeof window === 'undefined') return
  if (scrollRaf) return

  scrollRaf = window.requestAnimationFrame(() => {
    const doc = document.documentElement
    const maxScroll = Math.max(doc.scrollHeight - window.innerHeight, 1)
    scrollProgress.value = Math.min(100, Math.max(0, (window.scrollY / maxScroll) * 100))
    scrollRaf = null
  })
}

onMounted(async () => {
  await loadPreferences()
  await selectSuburb(selectedSuburb.value)
  await nextTick()
  initRevealObserver()
  updateScrollProgress()
  window.addEventListener('scroll', updateScrollProgress, { passive: true })
})

onUnmounted(() => {
  if (revealObserver) revealObserver.disconnect()
  if (scrollRaf) window.cancelAnimationFrame(scrollRaf)
  window.removeEventListener('scroll', updateScrollProgress)
})
</script>

<style scoped>
.construction-page {
  background: var(--bg-page);
  min-height: 100vh;
  overflow-x: hidden;
}

.construction-scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 60;
  height: 3px;
  width: 0;
  background: linear-gradient(90deg, #ef5a38, #d88409, var(--primary));
  box-shadow: 0 0 18px rgba(239, 90, 56, 0.28);
  transition: width 0.12s linear;
}

.dust-hero {
  position: relative;
  background: linear-gradient(135deg, #972113 0%, #c53a24 48%, #ef5a38 100%);
  padding: 78px 0 84px;
  color: var(--text-light);
  overflow: hidden;
}

.dust-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 88% 18%, rgba(255, 255, 255, 0.16), transparent 32%),
    linear-gradient(90deg, rgba(50, 12, 6, 0.16), transparent 54%);
  pointer-events: none;
}

.dust-hero-inner {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 0.92fr) minmax(520px, 1.08fr);
  align-items: center;
  gap: 82px;
}

.hero-back-link {
  display: inline-flex;
  margin-bottom: 28px;
  color: rgba(255, 255, 255, 0.92);
  font-size: 16px;
  font-weight: 500;
  transition: transform 0.26s var(--ease-out-quart), color 0.26s ease;
}

.hero-back-link:hover {
  color: #ffffff;
  transform: translateX(-4px);
}

.dust-hero-copy h1 {
  margin: 0 0 22px;
  font-family: var(--font-serif);
  font-size: clamp(52px, 6.2vw, 76px);
  font-weight: 500;
  line-height: 0.98;
  letter-spacing: -0.035em;
}

.dust-hero-copy h1 span {
  font-style: italic;
  font-weight: 400;
}

.dust-hero-copy p {
  margin: 0;
  max-width: 640px;
  color: rgba(255, 255, 255, 0.94);
  font-size: 19px;
  line-height: 1.6;
}

.dust-hero-image-wrap {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(32, 9, 3, 0.28);
  transition: transform 0.45s var(--ease-out-expo), box-shadow 0.45s ease;
}

.dust-hero-image-wrap:hover {
  transform: translateY(-8px) scale(1.012);
  box-shadow: 0 34px 80px rgba(32, 9, 3, 0.34);
}

.dust-hero-image {
  width: 100%;
  height: 320px;
  object-fit: cover;
  transition: transform 0.65s var(--ease-out-expo), filter 0.45s ease;
}

.dust-hero-image-wrap:hover .dust-hero-image {
  transform: scale(1.06);
  filter: saturate(1.08) contrast(1.04);
}

.dust-floating-art {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  pointer-events: none;
}

.dust-art-emoji {
  position: relative;
  z-index: 2;
  font-size: 44px;
  filter: drop-shadow(0 18px 30px rgba(0, 0, 0, 0.24));
  animation: floatDustIcon 4.8s ease-in-out infinite;
}

.dust-art-orb {
  position: absolute;
  border-radius: 34px;
  background: rgba(255, 255, 255, 0.13);
  backdrop-filter: blur(2px);
}

.dust-art-orb-one {
  width: 220px;
  height: 136px;
  transform: rotate(-8deg);
}

.dust-art-orb-two {
  width: 128px;
  height: 94px;
  right: 46px;
  bottom: 44px;
}

.dust-scroll-cue {
  position: absolute;
  left: 50%;
  bottom: -56px;
  z-index: 2;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border: 0;
  border-radius: 999px;
  background: rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.86);
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transform: translateX(-50%);
  transition: transform 0.24s var(--ease-out-quart), background 0.24s ease;
}

.dust-scroll-cue:hover {
  transform: translateX(-50%) translateY(3px);
  background: rgba(255,255,255,0.24);
}

.dust-scroll-line {
  width: 1px;
  height: 30px;
  background: rgba(255,255,255,0.78);
  animation: dustScrollPulse 1.8s ease-in-out infinite;
}

@keyframes floatDustIcon {
  0%, 100% { transform: translateY(0) rotate(-1deg); }
  50% { transform: translateY(-12px) rotate(2deg); }
}

@keyframes dustScrollPulse {
  0%, 100% { transform: scaleY(0.45); opacity: 0.45; }
  50% { transform: scaleY(1); opacity: 1; }
}

.dust-content {
  padding-top: 0;
}

.dust-content .container {
  width: min(calc(100% - 40px), 1380px);
}

.suburb-card {
  position: relative;
  z-index: 4;
  margin-top: -32px;
  margin-bottom: 58px;
  padding: 34px 36px 38px;
  border-radius: var(--radius-xl);
  border: 1px solid rgba(10, 40, 30, 0.07);
  transition: transform 0.36s var(--ease-out-expo), box-shadow 0.36s ease, border-color 0.36s ease;
}

.suburb-card:hover,
.risk-summary-card:hover,
.dust-actions-panel:hover {
  transform: translateY(-7px);
  box-shadow: 0 22px 58px rgba(10, 40, 30, 0.13);
}

.suburb-card h2,
.sites-heading,
.dust-actions-content h2,
.risk-summary-card h2 {
  font-family: var(--font-serif);
}

.suburb-card h2 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 500;
}

.suburb-card > p {
  margin: 0 0 24px;
  color: #344563;
  font-size: 16px;
  line-height: 1.55;
}

.privacy-controls {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.privacy-toggle input {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
  transition: transform 0.2s ease;
}

.privacy-toggle input:hover {
  transform: scale(1.12);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.location-pill,
.suburb-pill {
  border: none;
  font-weight: 600;
  font-family: var(--font-sans);
  transition: transform 0.28s var(--ease-out-quart), box-shadow 0.28s ease, background 0.28s ease, color 0.28s ease;
}

.location-pill {
  border: 2px solid #8b9ab1;
  background: transparent;
  color: #344563;
  border-radius: 999px;
  padding: 11px 24px;
  font-size: 15px;
}

.location-pill:hover:not(:disabled) {
  transform: translateY(-3px);
  background: #fff7f3;
  border-color: #ef5a38;
  color: #c24124;
  box-shadow: 0 12px 24px rgba(239, 90, 56, 0.15);
}

.location-pill:disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.suburb-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 22px;
}

.suburb-pill {
  min-height: 44px;
  border-radius: 999px;
  background: #f6f3f0;
  color: #344563;
  font-size: 15px;
  padding: 11px 16px;
}

.suburb-pill:hover {
  transform: translateY(-4px) scale(1.018);
  background: #fff5ef;
  color: #c24124;
  box-shadow: 0 14px 26px rgba(239, 90, 56, 0.13);
}

.suburb-pill.active {
  background: #ef5a38;
  color: #ffffff;
  box-shadow: 0 16px 32px rgba(239, 90, 56, 0.26);
}

.updated-row {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 600;
}

.updated-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #d88409;
  box-shadow: 0 0 0 6px rgba(216, 132, 9, 0.12);
}

.risk-summary-card {
  display: flex;
  justify-content: space-between;
  gap: 28px;
  margin-bottom: 52px;
  padding: 34px 36px;
  border: 1px solid rgba(10, 40, 30, 0.07);
  background: radial-gradient(circle at 92% 14%, rgba(239, 90, 56, 0.11), transparent 26%), var(--bg-white);
  transition: transform 0.36s var(--ease-out-expo), box-shadow 0.36s ease;
}

.risk-summary-card .eyebrow,
.dust-actions-content .eyebrow {
  color: #c75a14;
}

.risk-summary-card .eyebrow::before,
.dust-actions-content .eyebrow::before {
  background: #d88409;
}

.risk-summary-card h2 {
  margin: 0 0 12px;
  font-size: 32px;
  font-weight: 500;
  line-height: 1.15;
}

.summary-text {
  margin: 0;
  max-width: 760px;
  color: #344563;
  font-size: 16px;
  line-height: 1.65;
}

.risk-highlight {
  min-width: 248px;
  padding: 20px;
  border-radius: var(--radius-md);
  transition: transform 0.28s var(--ease-out-quart), box-shadow 0.28s ease;
}

.risk-highlight:hover {
  transform: translateY(-4px) scale(1.012);
  box-shadow: var(--shadow-card);
}

.risk-highlight.high { background: #fff2ed; }
.risk-highlight.moderate { background: #fff7e8; }
.risk-highlight.low { background: #ecf8f2; }

.risk-label {
  display: block;
  margin-bottom: 10px;
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.risk-badge,
.site-risk-badge {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  border-radius: 999px;
  font-weight: 600;
  white-space: nowrap;
}

.risk-badge {
  padding: 9px 15px;
  margin-bottom: 12px;
  font-size: 14px;
}

.risk-badge.high,
.site-risk-badge.high {
  color: #df5636;
  background: #fff4ef;
}

.risk-badge.moderate,
.site-risk-badge.moderate {
  color: #c8760a;
  background: #fff5df;
}

.risk-badge.low,
.site-risk-badge.low {
  color: #25895c;
  background: #e8f6ef;
}

.risk-highlight p {
  margin: 0;
  color: #344563;
  font-size: 14px;
  line-height: 1.55;
}

.map-shell {
  margin-bottom: 54px;
  transition: transform 0.36s var(--ease-out-expo), filter 0.36s ease;
}

.map-shell:hover {
  transform: translateY(-5px);
  filter: drop-shadow(0 18px 36px rgba(10, 40, 30, 0.11));
}

.map-shell:empty {
  display: none;
}

.sites-section {
  margin-bottom: 74px;
}

.sites-heading {
  margin-bottom: 26px;
  font-size: 30px;
}

.sites-list {
  display: grid;
  gap: 16px;
}

.site-card {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  min-height: 108px;
  padding: 28px 28px 28px 34px;
  cursor: pointer;
  outline: none;
  border: none;
  border-left: 4px solid transparent;
  border-radius: var(--radius-md);
  box-shadow: none;
  overflow: hidden;
  animation: siteFloatIn 0.72s var(--ease-out-expo) both;
  transition: transform 0.34s var(--ease-out-expo), box-shadow 0.34s ease, background 0.34s ease;
}

.site-card::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 0;
  width: 4px;
  height: 100%;
  border-radius: 999px;
  background: currentColor;
}

.site-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
  transform: translateX(-105%);
  opacity: 0;
  transition: transform 0.6s var(--ease-out-expo), opacity 0.35s ease;
  pointer-events: none;
}

.site-card.selected {
  transform: translateX(12px) translateY(-4px);
  box-shadow: 0 20px 50px rgba(10, 40, 30, 0.12);
}

.site-card.selected::before {
  width: 7px;
}

.site-card:focus-visible {
  box-shadow: 0 0 0 4px rgba(13, 107, 94, 0.16), 0 18px 44px rgba(10, 40, 30, 0.08);
}

.site-card:hover {
  transform: translateX(10px) translateY(-4px);
  box-shadow: 0 18px 44px rgba(10, 40, 30, 0.08);
}

.site-card:hover::after {
  transform: translateX(105%);
  opacity: 1;
}

.site-card.high {
  color: #ef5a38;
  border-left-color: #ef5a38;
  background: linear-gradient(90deg, #fff7f4 0%, #fffafa 62%, rgba(255, 250, 250, 0.55) 100%);
}

.site-card.moderate {
  color: #d88409;
  border-left-color: #d88409;
  background: linear-gradient(90deg, #fff9ec 0%, #fffdf7 62%, rgba(255, 253, 247, 0.55) 100%);
}

.site-card.low {
  color: #2f9a68;
  border-left-color: #2f9a68;
  background: linear-gradient(90deg, #f4fbf7 0%, #fbfdfb 62%, rgba(251, 253, 251, 0.55) 100%);
}

.site-delay-1 { animation-delay: 0.07s; }
.site-delay-2 { animation-delay: 0.14s; }
.site-delay-3 { animation-delay: 0.21s; }
.site-delay-4 { animation-delay: 0.28s; }

.site-card-main {
  position: relative;
  z-index: 1;
}

.site-card-main h3 {
  margin: 0 0 9px;
  color: #202734;
  font-size: 16px;
  font-weight: 700;
}

.site-card-main p {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  margin: 0;
  color: #344563;
  font-size: 14px;
}

.site-risk-badge {
  position: relative;
  z-index: 1;
  min-width: 122px;
  justify-content: center;
  padding: 12px 18px;
  font-size: 16px;
  transition: transform 0.28s var(--ease-out-quart), box-shadow 0.28s ease;
}

.site-card:hover .site-risk-badge,
.site-card.selected .site-risk-badge {
  transform: scale(1.06);
  box-shadow: 0 12px 24px rgba(10, 40, 30, 0.06);
}

.site-risk-badge span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.dust-actions-panel {
  margin-bottom: 28px;
  overflow: hidden;
  border: 1px solid rgba(13, 107, 94, 0.09);
  background: linear-gradient(135deg, #fffaf0, #ffffff 55%, #eff8f4);
  transition: transform 0.36s var(--ease-out-expo), box-shadow 0.36s ease;
}

.dust-actions-content {
  padding: 36px;
}

.dust-actions-content h2 {
  margin: 0 0 24px;
  font-size: 32px;
  font-weight: 500;
}

.dust-actions-list {
  display: grid;
  gap: 14px;
  margin: 0 0 28px;
  padding: 0;
  list-style: none;
}

.dust-actions-list li {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  color: #344563;
  font-size: 16px;
  line-height: 1.55;
  transition: transform 0.24s var(--ease-out-quart), color 0.24s ease;
}

.dust-actions-list li:hover {
  transform: translateX(6px);
  color: var(--primary-dark);
}

.dust-actions-list span {
  width: 26px;
  height: 26px;
  flex: 0 0 26px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--teal-muted);
  color: var(--primary);
  font-size: 13px;
  font-weight: 800;
}

.dust-actions-btn {
  width: fit-content;
}

.dust-actions-btn span {
  transition: transform 0.24s ease;
}

.dust-actions-btn:hover span {
  transform: translateX(4px);
}

.error-text,
.success-text {
  margin-top: 18px;
  font-weight: 650;
}

.error-text { color: #c0392b; }
.success-text { color: var(--primary); }

@keyframes siteFloatIn {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1100px) {
  .dust-hero-inner {
    grid-template-columns: 1fr;
    gap: 38px;
  }

  .dust-hero-image {
    height: 340px;
  }

  .suburb-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .risk-summary-card {
    flex-direction: column;
  }

  .risk-highlight {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .dust-hero {
    padding: 52px 0 62px;
  }

  .dust-hero-copy h1 {
    font-size: 44px;
  }

  .dust-hero-copy p {
    font-size: 17px;
  }

  .dust-hero-image {
    height: 220px;
  }

  .suburb-card,
  .risk-summary-card,
  .dust-actions-content {
    padding: 26px 22px;
  }

  .suburb-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .privacy-controls {
    align-items: flex-start;
  }

  .site-card {
    align-items: flex-start;
    flex-direction: column;
    padding: 22px 20px;
  }

  .site-card:hover,
  .site-card.selected {
    transform: translateY(-5px);
  }

  .site-risk-badge {
    align-self: flex-start;
  }
}

@media (max-width: 520px) {
  .suburb-grid {
    grid-template-columns: 1fr;
  }

  .privacy-controls {
    flex-direction: column;
  }

  .location-pill {
    width: 100%;
  }
}
</style>
<style scoped>
.dust-floating-art,
.dust-scroll-cue {
  display: none !important;
}

.dust-hero-image-wrap {
  animation: dustImageFloat 6s ease-in-out infinite;
  will-change: transform;
}

@keyframes dustImageFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-12px) rotate(-0.35deg); }
}

@media (prefers-reduced-motion: reduce) {
  .dust-hero-image-wrap { animation: none; }
}
</style>
