<template>
  <div class="scanner-page">

    <!-- ── How SafeShelf Works Modal ─────────────────────────── -->
    <transition name="modal-fade">
      <div v-if="showHowModal" class="modal-backdrop" @click.self="showHowModal = false">
        <div class="modal-box">
          <button class="modal-close" @click="showHowModal = false">✕</button>
          <h2>How SafeShelf protects your family</h2>
          <p class="modal-lead">Many everyday cleaning products contain chemicals that trigger asthma in children — but they're buried in ingredient lists most parents never read. SafeShelf reads them for you, instantly.</p>

          <div class="how-steps">
            <div class="how-step" v-for="(step, i) in howSteps" :key="i">
              <div class="how-step__num">{{ i + 1 }}</div>
              <div>
                <strong>{{ step.title }}</strong>
                <p>{{ step.desc }}</p>
              </div>
            </div>
          </div>

          <button class="btn-got-it" @click="showHowModal = false">Got it — start scanning</button>
        </div>
      </div>
    </transition>

    <main>
      <!-- ── Hero ──────────────────────────────────────────────── -->
      <section class="hero">
        <div class="hero__inner">
          <p class="hero__eyebrow">AI-POWERED SAFESHELF</p>
          <h1 class="hero__title">
            Before it goes in your trolley, know <em>what's inside.</em>
          </h1>
          <p class="hero__sub">One scan tells you if a product contains ingredients that could trigger your child's asthma.</p>

          <button class="btn-how" @click="showHowModal = true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            How SafeShelf helps your family
          </button>

          <!-- 3-step visual -->
          <div class="hero__steps">
            <div class="hero__steps-row">
              <div class="hero__step-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="9" y1="7" x2="15" y2="7"/><line x1="9" y1="11" x2="15" y2="11"/><line x1="9" y1="15" x2="12" y2="15"/></svg>
              </div>
              <div class="hero__step-connector"></div>
              <div class="hero__step-icon barcode-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="3" height="16"/><rect x="7" y="4" width="1.5" height="16"/><rect x="10" y="4" width="3" height="16"/><rect x="15" y="4" width="1.5" height="16"/><rect x="19" y="4" width="3" height="16"/></svg>
              </div>
              <div class="hero__step-connector"></div>
              <div class="hero__step-icon danger-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><circle cx="12" cy="16" r="0.5" fill="currentColor"/></svg>
              </div>
            </div>

            <div class="hero__step-labels">
              <div class="hero__step-label">
                <span class="step-num">1</span>
                <strong>Find the product</strong>
                <small>Any household item</small>
              </div>
              <div class="hero__step-label">
                <span class="step-num">2</span>
                <strong>Scan the barcode</strong>
                <small>Type or photograph</small>
              </div>
              <div class="hero__step-label">
                <span class="step-num">3</span>
                <strong>See what's inside</strong>
                <small>Triggers highlighted</small>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Scan card ──────────────────────────────────────────── -->
      <section class="scan-section">
        <div class="scan-card">

          <!-- Tabs -->
          <div class="scan-tabs">
            <button
              class="scan-tab"
              :class="{ active: scanMode === 'image' }"
              type="button"
              @click="scanMode = 'image'"
            >Upload Photo</button>
            <button
              class="scan-tab"
              :class="{ active: scanMode === 'barcode' }"
              type="button"
              @click="scanMode = 'barcode'"
            >Barcode Number</button>
          </div>

          <!-- Image upload -->
          <div v-if="scanMode === 'image'" class="upload-area">
            <label for="barcode-image" class="upload-dropzone" :class="{ 'has-file': selectedFile }">
              <div class="upload-dropzone__inner">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                <strong>{{ selectedFileName || 'Upload barcode photo' }}</strong>
                <small>JPG or PNG — barcode read automatically</small>
              </div>
              <input
                id="barcode-image"
                class="upload-input"
                accept="image/*"
                type="file"
                @change="handleFileChange"
              />
            </label>

            <button
              class="btn-scan"
              type="button"
              :disabled="isLoading || !selectedFile"
              @click="submitImage"
            >
              <span v-if="isLoading" class="spinner"></span>
              {{ isLoading ? 'Scanning…' : 'Scan Photo' }}
            </button>
          </div>

          <!-- Barcode input -->
          <div v-else class="barcode-area">
            <div class="barcode-input-row">
              <input
                id="barcode-input"
                v-model.trim="barcodeInput"
                class="barcode-input"
                inputmode="numeric"
                pattern="[0-9]*"
                placeholder="e.g. 8710447451922"
                type="text"
                @keydown.enter.prevent="submitBarcode"
              />
              <button
                class="btn-scan btn-scan--inline"
                type="button"
                :disabled="isLoading"
                @click="submitBarcode"
              >
                <span v-if="isLoading" class="spinner"></span>
                {{ isLoading ? 'Checking…' : 'Check' }}
              </button>
            </div>
          </div>

          <p v-if="formError" class="form-error">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><circle cx="12" cy="16" r="0.5" fill="currentColor"/></svg>
            {{ formError }}
          </p>
        </div>

      </section>

      <!-- ── Result section ────────────────────────────────────── -->
      <section v-if="showResult && scanResult" ref="resultSection" class="result-section">

        <!-- Product header -->
        <div class="result-header">
          <div class="result-header__left">
            <div class="result-found-badge">
              <span class="found-dot" :class="scanResult.found ? 'found' : 'not-found'"></span>
              {{ resultStatusLabel }}
            </div>
            <div class="result-product-row">
              <div class="result-product-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
              </div>
              <div>
                <h2 class="result-product-name">{{ productName }}</h2>
                <p class="result-product-meta">{{ productMeta }}</p>
              </div>
            </div>
          </div>
          <button class="btn-scan-next" @click="resetScan">Scan next product</button>
        </div>

        <div v-if="scanResult.found" class="result-body">

          <!-- Left col: gauge + stats + advice -->
          <div class="result-left">
            <div class="gauge-card">
              <!-- Arc gauge SVG -->
              <div class="gauge-wrap">
                <svg viewBox="0 0 200 120" class="gauge-svg">
                  <defs>
                    <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%"   stop-color="#11915d"/>
                      <stop offset="50%"  stop-color="#d97706"/>
                      <stop offset="100%" stop-color="#ea2951"/>
                    </linearGradient>
                  </defs>
                  <!-- Track -->
                  <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#f0ece6" stroke-width="16" stroke-linecap="round"/>
                  <!-- Fill -->
                  <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#gaugeGrad)" stroke-width="16" stroke-linecap="round"
                    :stroke-dasharray="`${gaugePercent * 2.51} 251`"
                    stroke-dashoffset="0"
                    style="transition: stroke-dasharray 1s cubic-bezier(.4,0,.2,1)"
                  />
                  <!-- Needle dot -->
                  <circle :cx="gaugeDotX" :cy="gaugeDotY" r="7" fill="white" stroke="#1a1a1a" stroke-width="2.5"/>
                </svg>
                <div class="gauge-label">
                  <strong :class="'gauge-risk-' + riskClass">{{ riskLabel }}</strong>
                  <span>{{ riskClass === 'none' ? 'No triggers' : 'Risk' }}</span>
                </div>
              </div>

              <!-- Stats row -->
              <div class="gauge-stats">
                <div class="gauge-stat">
                  <strong>{{ triggerList.length }}</strong>
                  <span>triggers</span>
                </div>
                <div class="gauge-stat-divider"></div>
                <div class="gauge-stat">
                  <strong>{{ checkedIngredientCount }}</strong>
                  <span>checked</span>
                </div>
                <div class="gauge-stat-divider"></div>
                <div class="gauge-stat">
                  <strong>{{ safeIngredientCount }}</strong>
                  <span>safe</span>
                </div>
              </div>

              <!-- Advice banner -->
              <div class="advice-banner" :class="'advice-' + riskClass">
                {{ scanResult.analysis.advice }}
              </div>
            </div>
          </div>

          <!-- Right col: safe ingredients + triggers + alternatives -->
          <div class="result-right">
            <div v-if="isEstimatedResult" class="source-note-card">
              <p class="block-eyebrow">ESTIMATED INGREDIENTS</p>
              <p>
                We could not find a full ingredient list for this exact product, so this result is based on common
                ingredients for its product category.
              </p>
            </div>

            <!-- Safe ingredients -->
            <div v-if="safeIngredients.length" class="safe-ingredients-block">
              <p class="block-eyebrow">{{ ingredientBlockLabel }}</p>
              <div class="safe-pills">
                <span v-for="ing in safeIngredients.slice(0, 8)" :key="ing" class="safe-pill">{{ ing }}</span>
              </div>
            </div>

            <!-- Triggers -->
            <div v-if="triggerList.length" class="triggers-block">
              <p class="block-eyebrow triggers-eyebrow">TRIGGERS DETECTED — TAP EACH TO LEARN MORE</p>
              <div class="triggers-list">
                <div
                  v-for="trigger in triggerList"
                  :key="`${trigger.ingredient}-${trigger.category}`"
                  class="trigger-row"
                  :class="{ expanded: expandedTrigger === trigger.ingredient }"
                  @click="toggleTrigger(trigger.ingredient)"
                >
                  <div class="trigger-row__header">
                    <div class="trigger-row__left">
                      <span class="trigger-dot" :class="trigger.level"></span>
                      <strong>{{ trigger.ingredient }}</strong>
                    </div>
                    <div class="trigger-row__right">
                      <span class="trigger-badge" :class="trigger.level">
                        {{ trigger.level === 'high' ? 'High risk' : trigger.level === 'medium' ? 'Medium risk' : 'Low risk' }}
                      </span>
                      <svg class="trigger-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <polyline :points="expandedTrigger === trigger.ingredient ? '18 15 12 9 6 15' : '6 9 12 15 18 9'"/>
                      </svg>
                    </div>
                  </div>
                  <transition name="expand">
                    <p v-if="expandedTrigger === trigger.ingredient" class="trigger-row__note">{{ trigger.note }}</p>
                  </transition>
                </div>
              </div>
            </div>

            <div v-else class="no-triggers">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
              {{ noTriggersMessage }}
            </div>

            <!-- Alternative ingredients -->
            <div v-if="alternativeSwaps.length" class="alternatives-block">
              <p class="block-eyebrow alt-eyebrow">LOOK FOR ALTERNATIVE INGREDIENTS</p>
              <ul class="alt-list">
                <li v-for="swap in alternativeSwaps" :key="swap.label">
                  <span class="alt-dot"></span>
                  <span><strong>{{ swap.label }}:</strong> {{ swap.tip }}</span>
                </li>
                <li>
                  <span class="alt-dot"></span>
                  <span><strong>General rule:</strong> Fewer ingredients = lower risk of hidden triggers</span>
                </li>
              </ul>
            </div>

            <div v-if="canUploadProductPhoto" class="product-upload-card">
              <p class="block-eyebrow">HELP IMPROVE THIS RESULT</p>
              <h3>Upload a product photo</h3>
              <p>
                Send a clear front or ingredient-label photo so the team can review it and improve this product entry.
              </p>
              <label class="product-photo-dropzone">
                <span>{{ productPhotoName || 'Choose product photo' }}</span>
                <input accept="image/*" type="file" @change="handleProductPhotoChange" />
              </label>
              <button
                class="btn-upload-product"
                type="button"
                :disabled="isUploadingPhoto || !productPhotoFile"
                @click="submitProductPhoto"
              >
                <span v-if="isUploadingPhoto" class="spinner"></span>
                {{ isUploadingPhoto ? 'Uploading...' : 'Upload product photo' }}
              </button>
              <p v-if="uploadMessage" class="upload-feedback upload-feedback--success">{{ uploadMessage }}</p>
              <p v-if="uploadError" class="upload-feedback upload-feedback--error">{{ uploadError }}</p>
            </div>

          </div>
        </div>

        <!-- Not found state -->
        <div v-else class="not-found-body">
          <div class="not-found-icon">?</div>
          <div>
            <h3>Barcode not in database</h3>
            <p>{{ scanResult.message }}</p>
            <p class="not-found-barcode">{{ scanResult.barcode }}</p>
          </div>
        </div>

        <div v-if="canUploadProductPhoto && !scanResult.found" class="not-found-upload">
          <div class="product-upload-card">
            <p class="block-eyebrow">HELP ADD THIS PRODUCT</p>
            <h3>Upload a product photo</h3>
            <p>Send a clear product or ingredient-label photo so this barcode can be reviewed.</p>
            <label class="product-photo-dropzone">
              <span>{{ productPhotoName || 'Choose product photo' }}</span>
              <input accept="image/*" type="file" @change="handleProductPhotoChange" />
            </label>
            <button
              class="btn-upload-product"
              type="button"
              :disabled="isUploadingPhoto || !productPhotoFile"
              @click="submitProductPhoto"
            >
              <span v-if="isUploadingPhoto" class="spinner"></span>
              {{ isUploadingPhoto ? 'Uploading...' : 'Upload product photo' }}
            </button>
            <p v-if="uploadMessage" class="upload-feedback upload-feedback--success">{{ uploadMessage }}</p>
            <p v-if="uploadError" class="upload-feedback upload-feedback--error">{{ uploadError }}</p>
          </div>
        </div>


      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
// ── All original state & logic preserved exactly ─────────────────
const scanMode        = ref('image')
const showResult      = ref(false)
const resultSection   = ref(null)
const barcodeInput    = ref('')
const selectedFile    = ref(null)
const selectedFileName= ref('')
const scanResult      = ref(null)
const formError       = ref('')
const isLoading       = ref(false)
const productPhotoFile= ref(null)
const productPhotoName= ref('')
const uploadMessage   = ref('')
const uploadError     = ref('')
const isUploadingPhoto= ref(false)

// New UI state
const showHowModal    = ref(false)
const expandedTrigger = ref(null)

const API_BASE_URL    = import.meta.env.VITE_API_BASE_URL || 'https://d204zergykc1k6.cloudfront.net'
const MAX_IMAGE_SIDE  = 1400
const IMAGE_QUALITY   = 0.78
const MAX_UPLOAD_BYTES= 4 * 1024 * 1024

const howSteps = [
  { title: 'Scan any product', desc: 'Enter the barcode number or photograph the barcode on any household product — cleaning sprays, detergents, air fresheners, fabric softeners.' },
  { title: 'We cross-reference the ingredients', desc: 'Our AI checks every ingredient against a global database of known asthma-triggering chemicals, sensitisers, and fragrance allergens.' },
  { title: 'You get a clear result', desc: 'A plain-language risk rating tells you whether the product is safe, and which specific ingredients are flagged — with a brief explanation of why each one matters.' },
  { title: 'Find safer alternatives', desc: 'Where triggers are found, SafeShelf guides you toward the ingredient types to look for instead — so your next shop is a better one.' },
]

watch(scanMode, () => { formError.value = '' })

watch(showResult, async (visible) => {
  if (!visible) return
  await nextTick()
  resultSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
})


const buildApiUrl = (path) => `${API_BASE_URL.replace(/\/$/, '')}${path}`

const normalizeTrigger = (trigger = {}) => ({
  ingredient: trigger.ingredient || 'Unknown ingredient',
  category: trigger.category || 'trigger',
  level: trigger.level || 'low',
  note: trigger.note || 'This ingredient may affect sensitive users.',
})

const normalizeResult = (payload = {}) => {
  const product = { ...(payload.product || {}) }
  const typicalIngredients = Array.isArray(payload.typical_ingredients)
    ? payload.typical_ingredients
    : []
  const actualIngredients = Array.isArray(product.ingredients)
    ? product.ingredients
    : []
  const fallbackIngredients = typicalIngredients
    .map((item) => item.ingredient)
    .filter(Boolean)
  const ingredients = actualIngredients.length ? actualIngredients : fallbackIngredients
  const rawTriggers = Array.isArray(payload.analysis?.triggers)
    ? payload.analysis.triggers
    : typicalIngredients.filter((item) => item.is_trigger)

  return {
    ...payload,
    found: Boolean(payload.found),
    ingredients_source: payload.ingredients_source || (actualIngredients.length ? 'actual' : typicalIngredients.length ? 'typical' : 'none'),
    product: {
      name: product.name || '',
      brand: product.brand || '',
      categories: product.categories || payload.category || '',
      source: product.source || payload.data_origin || '',
      ingredients,
    },
    analysis: {
      risk_level: payload.analysis?.risk_level || 'none',
      risk_score: payload.analysis?.risk_score ?? 0,
      product_form: payload.analysis?.product_form || 'unknown',
      advice: payload.analysis?.advice || payload.message || 'No ingredient analysis is available yet.',
      triggers: rawTriggers.map(normalizeTrigger),
      is_estimate: Boolean(payload.analysis?.is_estimate || payload.ingredients_source === 'typical'),
    },
    typical_ingredients: typicalIngredients,
  }
}

// ── Computed (all original logic preserved) ──────────────────────
const productName = computed(() => {
  if (!scanResult.value?.found) return 'Unknown product'
  return scanResult.value.product.name || 'Unnamed product'
})

const productMeta = computed(() => {
  if (!scanResult.value?.found) return scanResult.value?.message || 'Product not in our database.'
  const parts = [scanResult.value.product.brand, sourceLabel.value].filter(Boolean)
  return parts.length ? parts.join(' — ') : `Barcode ${scanResult.value.barcode}`
})

const riskClass = computed(() => scanResult.value?.analysis?.risk_level || 'none')
const triggerList = computed(() => scanResult.value?.analysis?.triggers || [])
const ingredientsList = computed(() => scanResult.value?.product?.ingredients || [])
const isEstimatedResult = computed(() => scanResult.value?.ingredients_source === 'typical')
const checkedIngredientCount = computed(() => ingredientsList.value.length)
const safeIngredientCount = computed(() => Math.max(0, checkedIngredientCount.value - triggerList.value.length))
const canUploadProductPhoto = computed(() => Boolean(scanResult.value?.barcode) && scanResult.value?.ingredients_source !== 'actual')

const sourceLabel = computed(() => {
  if (!scanResult.value?.found) return ''
  if (scanResult.value.ingredients_source === 'actual') return scanResult.value.product.source || 'actual ingredients'
  if (scanResult.value.ingredients_source === 'typical') return 'category estimate'
  return 'ingredient list needed'
})

const resultStatusLabel = computed(() => {
  if (!scanResult.value?.found) return 'Product not found'
  if (scanResult.value.ingredients_source === 'typical') return 'Product found — estimated'
  if (scanResult.value.ingredients_source === 'none') return 'Product found — ingredients needed'
  return 'Product found'
})

const ingredientBlockLabel = computed(() => (
  isEstimatedResult.value ? 'COMMON INGREDIENTS FOR THIS CATEGORY' : 'SAFE INGREDIENTS'
))

const noTriggersMessage = computed(() => (
  isEstimatedResult.value
    ? 'No known asthma triggers detected in the common ingredients for this product category.'
    : 'No known asthma triggers detected in this product.'
))

const riskLabel = computed(() => {
  const labels = { high: 'High', medium: 'Medium', low: 'Low', none: 'None' }
  return labels[riskClass.value] || 'None'
})

const riskMeterWidth = computed(() => {
  const widths = { high: '100%', medium: '66%', low: '34%', none: '12%' }
  return widths[riskClass.value] || '12%'
})

// New computed for gauge arc
const gaugePercent = computed(() => {
  const map = { high: 100, medium: 66, low: 34, none: 12 }
  return map[riskClass.value] ?? 12
})

const gaugeDotX = computed(() => {
  const angle = Math.PI + (gaugePercent.value / 100) * Math.PI
  return 100 + 80 * Math.cos(angle)
})

const gaugeDotY = computed(() => {
  const angle = Math.PI + (gaugePercent.value / 100) * Math.PI
  return 100 + 80 * Math.sin(angle)
})

// Safe ingredients = all ingredients minus trigger names
const safeIngredients = computed(() => {
  if (!scanResult.value?.found) return []
  const triggerNames = new Set(triggerList.value.map(t => t.ingredient.toLowerCase()))
  return ingredientsList.value.filter(i => !triggerNames.has(i.toLowerCase()))
})

// Generate swap tips from triggers
const alternativeSwaps = computed(() => {
  if (!scanResult.value?.found) return []
  const triggers = triggerList.value
  const swaps = []
  const fragranceTriggers = triggers.filter(t => ['parfum', 'fragrance', 'limonene', 'linalool'].some(f => t.ingredient.toLowerCase().includes(f)))
  if (fragranceTriggers.length) swaps.push({ label: fragranceTriggers.map(t => t.ingredient).join(' / '), tip: 'Choose fragrance-free or unscented variants' })
  const allergenTriggers = triggers.filter(t => ['citronellol', 'geraniol', 'eugenol', 'benzyl'].some(f => t.ingredient.toLowerCase().includes(f)))
  if (allergenTriggers.length) swaps.push({ label: allergenTriggers.map(t => t.ingredient).join(' / '), tip: 'Look for products labelled allergen-free' })
  return swaps
})

function toggleTrigger(name) {
  expandedTrigger.value = expandedTrigger.value === name ? null : name
}

function resetScan() {
  showResult.value  = false
  scanResult.value  = null
  barcodeInput.value= ''
  selectedFile.value= null
  selectedFileName.value = ''
  productPhotoFile.value = null
  productPhotoName.value = ''
  uploadMessage.value = ''
  uploadError.value = ''
  formError.value   = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ── All original API/file logic preserved exactly ────────────────
const handleFileChange = (event) => {
  const file = event.target.files?.[0] || null
  selectedFile.value     = file
  selectedFileName.value = file?.name || ''
  formError.value        = ''
}

const loadImage = (file) =>
  new Promise((resolve, reject) => {
    const image    = new Image()
    const objectUrl= URL.createObjectURL(file)
    image.onload  = () => { URL.revokeObjectURL(objectUrl); resolve(image) }
    image.onerror = () => { URL.revokeObjectURL(objectUrl); reject(new Error('Could not read this image. Try a JPG or PNG barcode photo.')) }
    image.src = objectUrl
  })

const canvasToBlob = (canvas) =>
  new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => { if (blob) resolve(blob); else reject(new Error('Could not prepare this image for upload.')) },
      'image/jpeg', IMAGE_QUALITY
    )
  })

const compressImageForUpload = async (file) => {
  if (file.size <= MAX_UPLOAD_BYTES && file.type === 'image/jpeg') return file
  const image  = await loadImage(file)
  const scale  = Math.min(1, MAX_IMAGE_SIDE / Math.max(image.width, image.height))
  const width  = Math.max(1, Math.round(image.width  * scale))
  const height = Math.max(1, Math.round(image.height * scale))
  const canvas = document.createElement('canvas')
  canvas.width = width; canvas.height = height
  const context = canvas.getContext('2d')
  context.fillStyle = '#ffffff'
  context.fillRect(0, 0, width, height)
  context.drawImage(image, 0, 0, width, height)
  const blob = await canvasToBlob(canvas)
  if (blob.size > MAX_UPLOAD_BYTES) throw new Error('This image is still too large after compression. Try cropping closer to the barcode.')
  return new File([blob], 'barcode-upload.jpg', { type: 'image/jpeg' })
}

const applyResult = async (payload) => {
  scanResult.value = normalizeResult(payload)
  productPhotoFile.value = null
  productPhotoName.value = ''
  uploadMessage.value = ''
  uploadError.value = ''
  showResult.value = true
  await nextTick()
  resultSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const readResponse = async (response) => {
  const payload = await response.json().catch(() => ({}))
  if (response.status === 404 && payload.found === false) return payload
  if (!response.ok) throw new Error(payload.error || payload.message || `Request failed with status ${response.status}`)
  return payload
}

const submitBarcode = async () => {
  const barcode = barcodeInput.value.trim()
  if (!/^\d{8,14}$/.test(barcode)) { formError.value = 'Enter a barcode with 8 to 14 digits.'; return }
  try {
    isLoading.value  = true
    formError.value  = ''
    const response = await fetch(buildApiUrl(`/scanner/lookup?barcode=${encodeURIComponent(barcode)}`))
    await applyResult(await readResponse(response))
  } catch (error) {
    formError.value = error.message || 'Could not check this barcode right now.'
  } finally {
    isLoading.value = false
  }
}

const submitImage = async () => {
  if (!selectedFile.value) { formError.value = 'Choose a barcode image first.'; return }
  try {
    isLoading.value = true
    formError.value = ''
    const formData  = new FormData()
    const imageFile = await compressImageForUpload(selectedFile.value)
    formData.append('image', imageFile)
    const response = await fetch(buildApiUrl('/scanner/scan'), { method: 'POST', body: formData })
    await applyResult(await readResponse(response))
  } catch (error) {
    formError.value = error.message || 'Could not scan this image right now.'
  } finally {
    isLoading.value = false
  }
}

const handleProductPhotoChange = (event) => {
  const file = event.target.files?.[0] || null
  productPhotoFile.value = file
  productPhotoName.value = file?.name || ''
  uploadMessage.value = ''
  uploadError.value = ''
}

const submitProductPhoto = async () => {
  if (!scanResult.value?.barcode) { uploadError.value = 'Scan or enter a barcode first.'; return }
  if (!productPhotoFile.value) { uploadError.value = 'Choose a product photo first.'; return }

  try {
    isUploadingPhoto.value = true
    uploadMessage.value = ''
    uploadError.value = ''
    const imageFile = await compressImageForUpload(productPhotoFile.value)
    const formData = new FormData()
    formData.append('barcode', scanResult.value.barcode)
    formData.append('image', imageFile)

    const response = await fetch(buildApiUrl('/scanner/upload_product_image'), {
      method: 'POST',
      body: formData,
    })
    const payload = await readResponse(response)
    uploadMessage.value = payload.message || 'Thanks, your product photo has been uploaded.'
    productPhotoFile.value = null
    productPhotoName.value = ''
  } catch (error) {
    uploadError.value = error.message || 'Could not upload this product photo right now.'
  } finally {
    isUploadingPhoto.value = false
  }
}

onMounted(() => {

})

onUnmounted(() => {

})
</script>

<style scoped>
/* ── Base ───────────────────────────────────────────────────── */
.scanner-page {
  min-height: 100vh;
  color: var(--text-dark, #0f172a);
}



/* ── Modal ──────────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9999;
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
  padding: 40px 36px 32px;
  max-width: 540px;
  width: 100%;
  position: relative;
  box-shadow: 0 24px 80px rgba(10,30,20,0.22);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 16px; right: 16px;
  background: #f5f4f0;
  border: none;
  border-radius: 50%;
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px;
  cursor: pointer;
  color: #5a6b7a;
  transition: background 0.2s;
}
.modal-close:hover { background: #e8e6e0; }

.modal-box h2 {
  font-family: var(--font-serif, Georgia, serif);
  font-size: 26px;
  font-weight: 500;
  margin: 0 0 10px;
  color: var(--text-dark);
}

.modal-lead {
  font-size: 14px;
  color: #5a6b7a;
  line-height: 1.6;
  margin: 0 0 24px;
}

.how-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 24px;
}

.how-step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: #fafaf8;
  border: 1px solid rgba(10,40,30,0.07);
  border-radius: 14px;
  padding: 16px 18px;
}

.how-step__num {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: var(--primary, #0d6b5e);
  color: white;
  font-size: 13px;
  font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}

.how-step strong {
  display: block;
  font-size: 14px;
  color: var(--text-dark);
  margin-bottom: 4px;
}

.how-step p {
  margin: 0;
  font-size: 13px;
  color: #5a6b7a;
  line-height: 1.5;
}

.btn-got-it {
  width: 100%;
  padding: 15px;
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.btn-got-it:hover { transform: translateY(-2px); box-shadow: 0 10px 32px rgba(13,107,94,0.3); }

/* ── Hero ───────────────────────────────────────────────────── */
.hero {
  padding: 72px 24px 0;
  text-align: center;
}

.hero__inner {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.hero__eyebrow {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: var(--primary, #0d6b5e);
  margin: 0;
}

.hero__title {
  font-family: var(--font-serif, Georgia, serif);
  font-size: clamp(30px, 4.5vw, 50px);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin: 0;
  color: var(--text-dark);
}

.hero__title em {
  font-style: italic;
  color: var(--primary, #0d6b5e);
}

.hero__sub {
  font-size: 16px;
  color: #5a6b7a;
  line-height: 1.6;
  margin: 0;
  max-width: 480px;
}

.btn-how {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: white;
  border: 1.5px solid rgba(13,107,94,0.25);
  border-radius: 999px;
  padding: 10px 22px;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary, #0d6b5e);
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.btn-how:hover { border-color: var(--primary, #0d6b5e); box-shadow: 0 4px 16px rgba(13,107,94,0.15); transform: translateY(-1px); }

/* ── Hero steps visual ──────────────────────────────────────── */
.hero__steps {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px 0 0;
}

.hero__steps-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  width: 100%;
  max-width: 400px;
}

.hero__step-icon {
  width: 56px; height: 56px;
  border-radius: 16px;
  background: white;
  border: 1.5px solid rgba(10,40,30,0.1);
  box-shadow: 0 4px 16px rgba(10,40,30,0.07);
  display: flex; align-items: center; justify-content: center;
  color: #546e8a;
  flex-shrink: 0;
}

.hero__step-icon.barcode-icon { color: var(--primary, #0d6b5e); border-color: rgba(13,107,94,0.2); }
.hero__step-icon.danger-icon  { color: #ea2951; border-color: rgba(234,41,81,0.2); }

.hero__step-connector {
  flex: 1;
  height: 1.5px;
  background: linear-gradient(90deg, rgba(10,40,30,0.12), rgba(10,40,30,0.06));
  margin: 0 4px;
}

.hero__step-labels {
  display: flex;
  justify-content: space-between;
  width: 100%;
  max-width: 400px;
}

.hero__step-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 56px;
}

.step-num {
  width: 20px; height: 20px;
  border-radius: 50%;
  background: var(--primary, #0d6b5e);
  color: white;
  font-size: 11px;
  font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}

.hero__step-label strong {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-dark);
  text-align: center;
  line-height: 1.3;
}

.hero__step-label small {
  font-size: 10.5px;
  color: #9aabb8;
  text-align: center;
  line-height: 1.2;
}

/* ── Scan section ───────────────────────────────────────────── */
.scan-section {
  padding: 40px 24px 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.scan-card {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.8);
  box-shadow: 0 4px 32px rgba(10,40,30,0.1), 0 1px 0 rgba(255,255,255,0.6) inset;
  padding: 8px;
  width: 100%;
  max-width: 560px;
  overflow: hidden;
}

/* Tabs */
.scan-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #f7f5f1;
  border-radius: 14px;
  padding: 4px;
  gap: 4px;
  margin-bottom: 0;
}

.scan-tab {
  border: none;
  border-radius: 10px;
  padding: 11px 16px;
  background: transparent;
  font-size: 14px;
  font-weight: 600;
  color: #6b7a90;
  cursor: pointer;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
}
.scan-tab.active {
  background: white;
  color: var(--text-dark);
  box-shadow: 0 2px 8px rgba(10,40,30,0.08);
}

/* Upload area */
.upload-area {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-dropzone {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 140px;
  border: 2px dashed rgba(13,107,94,0.3);
  border-radius: 14px;
  background: #f7faf9;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  position: relative;
  overflow: hidden;
}
.upload-dropzone:hover, .upload-dropzone.has-file { border-color: var(--primary, #0d6b5e); background: #f0fdf8; }

.upload-dropzone__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #546e8a;
  pointer-events: none;
  padding: 20px;
  text-align: center;
}
.upload-dropzone__inner svg { color: var(--primary, #0d6b5e); opacity: 0.7; }
.upload-dropzone__inner strong { font-size: 14px; font-weight: 700; color: var(--primary, #0d6b5e); }
.upload-dropzone__inner small  { font-size: 12px; color: #9aabb8; }

.upload-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

/* Barcode input area */
.barcode-area {
  padding: 16px;
}

.barcode-input-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.barcode-input {
  flex: 1;
  min-height: 50px;
  border: 1.5px solid rgba(10,40,30,0.12);
  border-radius: 12px;
  padding: 0 16px;
  font: inherit;
  font-size: 15px;
  color: var(--text-dark);
  background: #f7f5f1;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.barcode-input:focus { background: white; border-color: var(--primary, #0d6b5e); box-shadow: 0 0 0 3px rgba(13,107,94,0.1); }
.barcode-input::placeholder { color: #9aabb8; }

/* Buttons */
.btn-scan {
  width: 100%;
  padding: 14px;
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  gap: 8px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s;
}
.btn-scan:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(13,107,94,0.28); }
.btn-scan:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-scan--inline { width: auto; padding: 14px 22px; border-radius: 12px; flex-shrink: 0; }

.form-error {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 16px 12px;
  padding: 11px 14px;
  background: #fff0eb;
  border: 1px solid rgba(234,41,81,0.15);
  border-radius: 10px;
  font-size: 13px;
  color: #c0321a;
  font-weight: 600;
}

/* Disclaimer */
.disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  max-width: 560px;
  font-size: 12.5px;
  color: #6b7a90;
  line-height: 1.55;
  background: white;
  border: 1px solid rgba(10,40,30,0.08);
  border-radius: 12px;
  padding: 12px 14px;
}
.disclaimer svg { flex-shrink: 0; margin-top: 1px; color: #9aabb8; }
.disclaimer--result { max-width: 100%; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 15px; height: 15px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

/* ── Result section ─────────────────────────────────────────── */
.result-section {
  padding: 0 24px 72px;
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Result header */
.result-header {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 20px;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 12px rgba(10,40,30,0.06);
}

.result-header__left { display: flex; flex-direction: column; gap: 10px; min-width: 0; }

.result-found-badge {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 700;
  color: #546e8a;
  letter-spacing: 0.02em;
}

.found-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.found-dot.found     { background: #11915d; box-shadow: 0 0 0 3px rgba(17,145,93,0.2); }
.found-dot.not-found { background: #ea2951; box-shadow: 0 0 0 3px rgba(234,41,81,0.2); }

.result-product-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.result-product-icon {
  width: 46px; height: 46px;
  border-radius: 12px;
  background: #f0fdf8;
  border: 1px solid rgba(13,107,94,0.15);
  display: flex; align-items: center; justify-content: center;
  color: var(--primary, #0d6b5e);
  flex-shrink: 0;
}

.result-product-name {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 2px;
  color: var(--text-dark);
  line-height: 1.2;
}

.result-product-meta {
  font-size: 12px;
  color: #9aabb8;
  margin: 0;
}

.btn-scan-next {
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.btn-scan-next:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(13,107,94,0.28); }

/* Result body */
.result-body {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  align-items: start;
}

/* Gauge card */
.gauge-card {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 20px;
  padding: 24px 20px;
  box-shadow: 0 2px 12px rgba(10,40,30,0.06);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.gauge-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  position: relative;
}

.gauge-svg {
  width: 100%;
  max-width: 200px;
  overflow: visible;
}

.gauge-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: -24px;
}

.gauge-label strong {
  font-size: 24px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.02em;
}
.gauge-label span {
  font-size: 12px;
  color: #9aabb8;
  font-weight: 600;
}

.gauge-risk-high     { color: #ea2951; }
.gauge-risk-medium   { color: #d97706; }
.gauge-risk-low      { color: #11915d; }
.gauge-risk-none     { color: #11915d; }

.gauge-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 14px 0;
  border-top: 1px solid rgba(10,40,30,0.06);
  border-bottom: 1px solid rgba(10,40,30,0.06);
}

.gauge-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.gauge-stat strong { font-size: 22px; font-weight: 800; color: var(--text-dark); line-height: 1; }
.gauge-stat span   { font-size: 11px; color: #9aabb8; font-weight: 600; }
.gauge-stat-divider { width: 1px; height: 32px; background: rgba(10,40,30,0.08); }

.advice-banner {
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.5;
  text-align: center;
}
.advice-high   { background: #fff0f3; color: #c0192e; }
.advice-medium { background: #fef3c7; color: #92400e; }
.advice-low    { background: #ecfdf5; color: #0d6b5e; }
.advice-none   { background: #ecfdf5; color: #0d6b5e; }

/* Right column */
.result-right {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.source-note-card,
.product-upload-card,
.not-found-upload {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(13,107,94,0.14);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(10,40,30,0.04);
}

.source-note-card p:last-child,
.product-upload-card p {
  margin: 0;
  color: #5a6b7a;
  font-size: 13px;
  line-height: 1.55;
}

.product-upload-card h3 {
  margin: 0 0 6px;
  font-size: 16px;
  color: var(--text-dark);
}

.product-photo-dropzone {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 54px;
  margin: 12px 0 10px;
  border: 1.5px dashed rgba(13,107,94,0.32);
  border-radius: 12px;
  background: #f7faf9;
  color: var(--primary, #0d6b5e);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  text-align: center;
  padding: 10px 14px;
  position: relative;
  overflow: hidden;
}

.product-photo-dropzone input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.btn-upload-product {
  width: 100%;
  border: none;
  border-radius: 12px;
  padding: 12px 14px;
  background: var(--primary, #0d6b5e);
  color: white;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s, box-shadow 0.2s;
}

.btn-upload-product:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(13,107,94,0.22);
}

.btn-upload-product:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.upload-feedback {
  margin-top: 10px !important;
  padding: 10px 12px;
  border-radius: 10px;
  font-weight: 600;
}

.upload-feedback--success {
  background: #ecfdf5;
  color: #0d6b5e !important;
}

.upload-feedback--error {
  background: #fff0eb;
  color: #c0321a !important;
}

.block-eyebrow {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #a0aaba;
  margin: 0 0 10px;
}

/* Safe ingredients */
.safe-ingredients-block {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(10,40,30,0.04);
}

.safe-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.safe-pill {
  background: #f0fdf8;
  border: 1px solid rgba(17,145,93,0.15);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #0d6b5e;
}

/* Triggers */
.triggers-block {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(10,40,30,0.04);
}

.triggers-eyebrow { color: #ea2951; }

.triggers-list { display: flex; flex-direction: column; gap: 6px; }

.trigger-row {
  border: 1.5px solid rgba(10,40,30,0.07);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.trigger-row:hover { border-color: rgba(10,40,30,0.14); box-shadow: 0 2px 8px rgba(10,40,30,0.06); }
.trigger-row.expanded { border-color: rgba(10,40,30,0.14); }

.trigger-row__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  gap: 10px;
}

.trigger-row__left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.trigger-row__left strong { font-size: 14px; font-weight: 700; color: var(--text-dark); }

.trigger-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.trigger-dot.high   { background: #ea2951; }
.trigger-dot.medium { background: #d97706; }
.trigger-dot.low    { background: #11915d; }

.trigger-row__right { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }

.trigger-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
}
.trigger-badge.high   { background: #fff0f3; color: #ea2951; }
.trigger-badge.medium { background: #fef3c7; color: #d97706; }
.trigger-badge.low    { background: #ecfdf5; color: #11915d; }

.trigger-chevron { color: #9aabb8; transition: transform 0.2s; flex-shrink: 0; }

.trigger-row__note {
  padding: 0 14px 13px;
  margin: 0;
  font-size: 13px;
  color: #5a6b7a;
  line-height: 1.55;
  border-top: 1px solid rgba(10,40,30,0.06);
  padding-top: 11px;
}

.no-triggers {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #ecfdf5;
  border: 1px solid rgba(17,145,93,0.2);
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #0d6b5e;
}

/* Alternatives */
.alternatives-block {
  background: #f0fdf8;
  border: 1px solid rgba(13,107,94,0.15);
  border-radius: 16px;
  padding: 16px 18px;
}

.alt-eyebrow { color: var(--primary, #0d6b5e); }

.alt-list {
  list-style: none;
  padding: 0; margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alt-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  color: #3d4a63;
  line-height: 1.5;
}

.alt-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--primary, #0d6b5e);
  flex-shrink: 0;
  margin-top: 5px;
}

/* Not found */
.not-found-body {
  background: white;
  border: 1px solid rgba(10,40,30,0.08);
  border-radius: 20px;
  padding: 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  box-shadow: 0 2px 12px rgba(10,40,30,0.06);
}

.not-found-icon {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: #f5f4f0;
  font-size: 28px;
  font-weight: 800;
  color: #9aabb8;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.not-found-body h3 { margin: 0 0 6px; font-size: 18px; }
.not-found-body p  { margin: 0; font-size: 14px; color: #5a6b7a; }
.not-found-barcode { font-family: monospace; color: #9aabb8 !important; font-size: 13px !important; margin-top: 4px !important; }

.not-found-upload {
  margin-top: -2px;
}

/* ── Transitions ────────────────────────────────────────────── */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from,   .modal-fade-leave-to     { opacity: 0; }
.modal-fade-enter-active .modal-box { transition: transform 0.3s cubic-bezier(0.16,1,0.3,1); }
.modal-fade-enter-from   .modal-box { transform: translateY(20px) scale(0.97); }

.expand-enter-active, .expand-leave-active { transition: opacity 0.2s ease; }
.expand-enter-from,   .expand-leave-to     { opacity: 0; }

/* ── Responsive ─────────────────────────────────────────────── */
@media (max-width: 760px) {
  .hero { padding: 48px 16px 0; }
  .result-body { grid-template-columns: 1fr; }
  .result-header { flex-direction: column; align-items: flex-start; }
  .btn-scan-next { width: 100%; justify-content: center; }
  .scan-section  { padding: 32px 16px 48px; }
  .result-section { padding: 0 16px 48px; }
  .hero__steps-row { max-width: 320px; }
}
</style>
