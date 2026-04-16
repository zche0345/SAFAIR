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
})

const mapEl = ref(null)
let mapInstance = null
let markersLayer = null

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
    const radius = getRiskRadius(site.riskTone)

    const circle = L.circle([site.lat, site.lon], {
      color,
      fillColor: color,
      fillOpacity: 0.2,
      radius,
      weight: 2,
    })

    const marker = L.circleMarker([site.lat, site.lon], {
      radius: 8,
      color,
      fillColor: color,
      fillOpacity: 0.95,
      weight: 2,
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

    boundsPoints.push([site.lat, site.lon])
  })

  if (boundsPoints.length > 1) {
    mapInstance.fitBounds(boundsPoints, { padding: [40, 40] })
  } else {
    mapInstance.setView([props.centerLat, props.centerLon], 15)
  }
}

onMounted(() => {
  mapInstance = L.map(mapEl.value, {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView([props.centerLat, props.centerLon], 15)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
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
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.map-header h2 {
  margin: 0 0 10px;
  font-size: 32px;
  font-weight: 500;
  color: var(--text-dark);
}

.map-subtext {
  margin: 0;
  color: #5d6777;
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
  color: #4b5563;
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