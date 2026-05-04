<template>
  <div class="construction-map-card">
    <div class="map-header">
      <div>
        <p class="map-eyebrow">CONSTRUCTION RISK MAP</p>
        <h2>Construction risk around you</h2>
        <p class="map-subtext">
          Showing nearby construction sites around
          <strong>{{ centerLabel }}</strong>
        </p>
      </div>

      <div class="map-legend">
        <div class="legend-item">
          <span class="legend-dot high"></span>
          <span>High</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot moderate"></span>
          <span>Moderate</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot low"></span>
          <span>Low</span>
        </div>
      </div>
    </div>

    <div ref="mapEl" class="map-view"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  centerLat: {
    type: Number,
    required: true,
  },
  centerLon: {
    type: Number,
    required: true,
  },
  centerLabel: {
    type: String,
    default: 'selected area',
  },
  sites: {
    type: Array,
    default: () => [],
  },
  selectedSiteId: {
    type: [String, Number],
    default: null,
  },
})

const mapEl = ref(null)
let mapInstance = null
let markersLayer = null
const siteMarkerRefs = new Map()
const siteCircleRefs = new Map()

const getRiskColor = (riskTone) => {
  if (riskTone === 'high') return '#ea2951'
  if (riskTone === 'moderate') return '#d36c00'
  return '#11915d'
}

const getRiskRadius = (riskTone) => {
  if (riskTone === 'high') return 80
  if (riskTone === 'moderate') return 60
  return 45
}

const renderMapContent = () => {
  if (!mapInstance || !markersLayer) return

  markersLayer.clearLayers()
  siteMarkerRefs.clear()
  siteCircleRefs.clear()

  const boundsPoints = []

  // User/suburb center marker
  const centerMarker = L.circleMarker([props.centerLat, props.centerLon], {
    radius: 10,
    color: '#1d4ed8',
    fillColor: '#3b82f6',
    fillOpacity: 0.95,
    weight: 2,
  }).bindPopup(`<strong>${props.centerLabel}</strong>`)

  centerMarker.addTo(markersLayer)
  boundsPoints.push([props.centerLat, props.centerLon])

  // Construction site markers
  props.sites.forEach((site) => {
    if (
      typeof site.lat !== 'number' ||
      typeof site.lon !== 'number'
    ) {
      return
    }

    const color = getRiskColor(site.riskTone)
    const isSelected = props.selectedSiteId && String(props.selectedSiteId) === String(site.siteId)
    const radius = getRiskRadius(site.riskTone)

    const circle = L.circle([site.lat, site.lon], {
      color,
      fillColor: color,
      fillOpacity: isSelected ? 0.34 : 0.2,
      radius: isSelected ? radius * 1.9 : radius,
      weight: isSelected ? 4 : 2,
      opacity: isSelected ? 0.95 : 0.8,
    })

    const marker = L.circleMarker([site.lat, site.lon], {
      radius: isSelected ? 13 : 8,
      color: isSelected ? '#ffffff' : color,
      fillColor: color,
      fillOpacity: 0.98,
      weight: isSelected ? 4 : 2,
      className: isSelected ? 'selected-construction-marker' : '',
    })

    const popupHtml = `
      <div style="min-width: 180px;">
        <strong>${site.title || 'Construction site'}</strong><br/>
        <span>${site.type || 'Active construction work'}</span><br/>
        <span>${site.distance || ''}</span><br/>
        <strong>${site.riskLabel || ''}</strong>
      </div>
    `

    circle.bindPopup(popupHtml)
    marker.bindPopup(popupHtml)

    circle.addTo(markersLayer)
    marker.addTo(markersLayer)

    siteMarkerRefs.set(String(site.siteId), marker)
    siteCircleRefs.set(String(site.siteId), circle)

    boundsPoints.push([site.lat, site.lon])
  })

  if (boundsPoints.length > 1) {
    mapInstance.fitBounds(boundsPoints, { padding: [40, 40] })
  } else {
    mapInstance.setView([props.centerLat, props.centerLon], 15)
  }

  activateSelectedSite(false)
}

const activateSelectedSite = (shouldFly = true) => {
  if (!mapInstance || !props.selectedSiteId) return

  const selectedSite = props.sites.find(
    (site) => String(site.siteId) === String(props.selectedSiteId)
  )

  if (!selectedSite || typeof selectedSite.lat !== 'number' || typeof selectedSite.lon !== 'number') return

  const marker = siteMarkerRefs.get(String(selectedSite.siteId))
  const latLng = [selectedSite.lat, selectedSite.lon]

  const openSelectedPopup = () => {
    marker?.openPopup()
  }

  if (shouldFly) {
    mapInstance.flyTo(latLng, Math.max(mapInstance.getZoom(), 16), {
      duration: 0.75,
      easeLinearity: 0.25,
    })
    mapInstance.once('moveend', openSelectedPopup)
    window.setTimeout(openSelectedPopup, 850)
    return
  }

  window.setTimeout(openSelectedPopup, 180)
}

onMounted(() => {
  mapInstance = L.map(mapEl.value, {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView([props.centerLat, props.centerLon], 15)

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OSM</a> © <a href="https://carto.com/">CARTO</a>',
  }).addTo(mapInstance)

  markersLayer = L.layerGroup().addTo(mapInstance)

  renderMapContent()
})

watch(
  () => [props.centerLat, props.centerLon, props.sites],
  () => {
    renderMapContent()
  },
  { deep: true }
)

watch(
  () => props.selectedSiteId,
  () => {
    renderMapContent()
    activateSelectedSite(true)
  }
)

onBeforeUnmount(() => {
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }
})
</script>

<style scoped>
.construction-map-card {
  background: white;
  border-radius: 30px;
  box-shadow: var(--shadow-soft);
  padding: 30px;
  margin-bottom: 52px;
}

.map-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 20px;
}

.map-eyebrow {
  margin: 0 0 8px;
  color: #ef2f55;
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.map-header h2 {
  margin: 0 0 10px;
  font-family: var(--font-serif);
  font-size: 32px;
  font-weight: 500;
  color: var(--text-dark);
}

.map-subtext {
  margin: 0;
  font-family: var(--font-sans);
  color: var(--text-muted);
  font-size: 16px;
  line-height: 1.6;
}

.map-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  align-items: center;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-sans);
  color: var(--text-body);
  font-size: 14px;
  font-weight: 600;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  display: inline-block;
}

.legend-dot.high {
  background: #ea2951;
}

.legend-dot.moderate {
  background: #d36c00;
}

.legend-dot.low {
  background: #11915d;
}

:deep(.selected-construction-marker) {
  filter: drop-shadow(0 0 14px rgba(234, 41, 81, 0.45)) drop-shadow(0 4px 12px rgba(10, 40, 30, 0.26));
}

.map-view {
  width: 100%;
  height: 420px;
  border-radius: 24px;
  overflow: hidden;
}

@media (max-width: 768px) {
  .construction-map-card {
    padding: 22px;
  }

  .map-header {
    flex-direction: column;
  }

  .map-header h2 {
    font-size: 26px;
  }

  .map-view {
    height: 320px;
  }
}
</style>