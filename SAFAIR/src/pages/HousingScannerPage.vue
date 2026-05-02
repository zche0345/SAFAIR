<template>
  <div class="scanner-page">
    <div class="scroll-progress" :style="{ width: scrollProgress + '%' }"></div>

    <main>
      <section class="scanner-hero">
        <div class="container scanner-hero__inner">
          <div class="scanner-hero__copy reveal visible">
            <RouterLink to="/" class="back-link">← Back to Home</RouterLink>

            <h1 class="scanner-hero__title">
              Asthma-Safe <span>Housing</span> Scanner
            </h1>

            <p class="scanner-hero__text">
              Check if cleaning products and household items contain asthma triggers before you buy.
            </p>
          </div>

          <div class="scanner-hero__visual reveal visible reveal-delay-1">
            <img
              class="scanner-hero__image"
              src="@/assets/images/product-scanner-hero.jpg"
              alt="Clean household shelf with plants and cleaning products"
            />
          </div>
        </div>
      </section>

      <section class="scanner-content">
        <div class="container scanner-grid">
          <article class="card scan-card reveal visible">
            <h2 class="scanner-section-title">Check a product</h2>
            <p class="muted scan-card__intro">Enter the barcode number or upload a clear barcode photo.</p>

            <div class="scan-tabs" aria-label="Scan method options">
              <button
                class="scan-tab"
                :class="{ active: scanMode === 'barcode' }"
                type="button"
                @click="scanMode = 'barcode'"
              >
                Barcode Number
              </button>
              <button
                class="scan-tab"
                :class="{ active: scanMode === 'image' }"
                type="button"
                @click="scanMode = 'image'"
              >
                Barcode Image
              </button>
            </div>

            <ol class="scan-steps">
              <li v-for="step in currentSteps" :key="step">
                <span>{{ currentSteps.indexOf(step) + 1 }}</span>
                <p>{{ step }}</p>
              </li>
            </ol>

            <form v-if="scanMode === 'barcode'" class="scanner-form" @submit.prevent="submitBarcode">
              <label class="scanner-label" for="barcode-input">Product barcode</label>
              <div class="scanner-input-row">
                <input
                  id="barcode-input"
                  v-model.trim="barcodeInput"
                  class="scanner-input"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  placeholder="e.g. 00000014"
                  type="text"
                />
                <button class="btn-pill btn-primary scanner-submit-btn" type="submit" :disabled="isLoading">
                  {{ isLoading ? 'Checking...' : 'Check' }}
                </button>
              </div>
            </form>

            <form v-else class="scanner-form" @submit.prevent="submitImage">
              <label class="scanner-label" for="barcode-image">Barcode image</label>
              <div class="phone-scan-box">
                <div class="phone-icon">📷</div>
                <strong>{{ selectedFileName || 'Upload a barcode photo' }}</strong>
                <small>JPG or PNG works best with a clear, straight barcode.</small>
                <input
                  id="barcode-image"
                  class="scanner-file"
                  accept="image/*"
                  type="file"
                  @change="handleFileChange"
                />
              </div>
              <button class="btn-pill btn-primary scanner-demo-btn" type="submit" :disabled="isLoading || !selectedFile">
                {{ isLoading ? 'Scanning...' : 'Scan Image' }}
              </button>
            </form>

            <p v-if="formError" class="scanner-error">{{ formError }}</p>
          </article>

          <article class="card preview-card reveal visible reveal-delay-1">
            <p class="preview-card__eyebrow">Product safety preview</p>

            <div class="preview-top">
              <div class="mock-phone">
                <div class="mock-phone__clip"></div>
                <div class="mock-phone__label">
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>

              <div class="ingredient-note">
                <strong>Ingredients:</strong>
                <p>
                  Water, Sodium Laureth Sulfate,
                  <mark class="danger">Chlorine Bleach</mark>,
                  Fragrance,
                  <mark class="warning">Limonene</mark>
                </p>
              </div>
            </div>

            <div class="camera-preview">
              <div class="camera-frame">
                <div class="camera-frame__box"></div>
                <div class="camera-frame__line"></div>
              </div>
            </div>

            <p class="preview-caption">
              SAFAIR checks product ingredients against known asthma-triggering chemicals.
            </p>
          </article>
        </div>
      </section>

      <section v-if="showResult && scanResult" ref="resultSection" class="scanner-result-section">
        <div class="container">
          <article class="card result-card reveal visible">
            <div class="result-card__top">
              <div class="result-product">
                <p class="eyebrow result-eyebrow">{{ scanResult.found ? 'Product found' : 'Product not found' }}</p>
                <div class="result-product__main">
                  <div class="product-icon">🧴</div>
                  <div>
                    <h2>{{ productName }}</h2>
                    <p class="muted">{{ productMeta }}</p>
                  </div>
                </div>
              </div>

              <div v-if="scanResult.found" class="score-box">
                <span>Risk Level</span>
                <strong>{{ riskLabel }}</strong>
                <small>{{ scanResult.barcode }}</small>
              </div>
            </div>

            <div v-if="scanResult.found" class="safety-meter">
              <div class="safety-meter__heading">
                <strong>Product Safety</strong>
                <span>{{ scanResult.analysis.advice }}</span>
              </div>
              <div class="safety-meter__track">
                <div class="safety-meter__fill" :class="riskClass" :style="{ width: riskMeterWidth }"></div>
              </div>
            </div>

            <div v-if="scanResult.found" class="trigger-section">
              <h3>Potential asthma triggers found</h3>

              <p v-if="!scanResult.analysis.triggers.length" class="muted">
                No known asthma triggers were detected in the available ingredient data.
              </p>

              <div
                v-for="trigger in scanResult.analysis.triggers"
                :key="`${trigger.ingredient}-${trigger.category}`"
                class="trigger-card"
                :class="trigger.level"
              >
                <span class="trigger-dot"></span>
                <div>
                  <strong>{{ trigger.ingredient }}</strong>
                  <p>{{ trigger.note }}</p>
                </div>
              </div>
            </div>

            <div v-if="scanResult.found" class="alternative-card">
              <p class="eyebrow">Ingredients checked</p>
              <h3>{{ scanResult.product.ingredients.length }} ingredients in database</h3>
              <p>{{ scanResult.analysis.advice }}</p>
            </div>

            <div v-else class="alternative-card">
              <p class="eyebrow">Barcode checked</p>
              <h3>{{ scanResult.barcode }}</h3>
              <p>{{ scanResult.message }}</p>
            </div>
          </article>
        </div>
      </section>
    </main>

  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

const scrollProgress = ref(0)
const scanMode = ref('barcode')
const showResult = ref(false)
const resultSection = ref(null)
const barcodeInput = ref('')
const selectedFile = ref(null)
const selectedFileName = ref('')
const scanResult = ref(null)
const formError = ref('')
const isLoading = ref(false)

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'https://d204zergykc1k6.cloudfront.net'

const barcodeSteps = [
  'Enter the barcode printed on the product',
  'SAFAIR will identify the product information',
  'Review asthma trigger warnings',
  'Use the result to compare safer alternatives'
]

const imageSteps = [
  'Upload a clear photo of the product barcode',
  'SAFAIR will identify the product information',
  'Review asthma trigger warnings',
  'Use the result to compare safer alternatives'
]

const currentSteps = ref(barcodeSteps)

watch(scanMode, (mode) => {
  currentSteps.value = mode === 'barcode' ? barcodeSteps : imageSteps
  formError.value = ''
})

watch(showResult, async (visible) => {
  if (!visible) return
  await nextTick()
  resultSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
})

const updateScrollProgress = () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
  scrollProgress.value = scrollHeight > 0 ? Math.min((scrollTop / scrollHeight) * 100, 100) : 0
}

const buildApiUrl = (path) => `${API_BASE_URL.replace(/\/$/, '')}${path}`

const productName = computed(() => {
  if (!scanResult.value?.found) return 'Unknown product'
  return scanResult.value.product.name || 'Unnamed product'
})

const productMeta = computed(() => {
  if (!scanResult.value?.found) return scanResult.value?.message || 'Product not in our database.'

  const parts = [scanResult.value.product.brand, scanResult.value.product.source]
    .filter(Boolean)

  return parts.length ? parts.join(' - ') : `Barcode ${scanResult.value.barcode}`
})

const riskClass = computed(() => scanResult.value?.analysis?.risk_level || 'none')

const riskLabel = computed(() => {
  const labels = {
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    none: 'None'
  }

  return labels[riskClass.value] || 'None'
})

const riskMeterWidth = computed(() => {
  const widths = {
    high: '100%',
    medium: '66%',
    low: '34%',
    none: '12%'
  }

  return widths[riskClass.value] || '12%'
})

const handleFileChange = (event) => {
  const file = event.target.files?.[0] || null
  selectedFile.value = file
  selectedFileName.value = file?.name || ''
  formError.value = ''
}

const applyResult = async (payload) => {
  scanResult.value = payload
  showResult.value = true
  await nextTick()
  resultSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const readResponse = async (response) => {
  const payload = await response.json().catch(() => ({}))

  if (response.status === 404 && payload.found === false) {
    return payload
  }

  if (!response.ok) {
    throw new Error(payload.error || payload.message || `Request failed with status ${response.status}`)
  }

  return payload
}

const submitBarcode = async () => {
  const barcode = barcodeInput.value.trim()
  if (!/^\d{8,14}$/.test(barcode)) {
    formError.value = 'Enter a barcode with 8 to 14 digits.'
    return
  }

  try {
    isLoading.value = true
    formError.value = ''
    const response = await fetch(buildApiUrl(`/scanner/lookup?barcode=${encodeURIComponent(barcode)}`))
    await applyResult(await readResponse(response))
  } catch (error) {
    formError.value = error.message || 'Could not check this barcode right now.'
  } finally {
    isLoading.value = false
  }
}

const submitImage = async () => {
  if (!selectedFile.value) {
    formError.value = 'Choose a barcode image first.'
    return
  }

  try {
    isLoading.value = true
    formError.value = ''
    const formData = new FormData()
    formData.append('image', selectedFile.value)

    const response = await fetch(buildApiUrl('/scanner/scan'), {
      method: 'POST',
      body: formData
    })

    await applyResult(await readResponse(response))
  } catch (error) {
    formError.value = error.message || 'Could not scan this image right now.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  updateScrollProgress()
  window.addEventListener('scroll', updateScrollProgress, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateScrollProgress)
})
</script>

<style scoped>
.scanner-page {
  min-height: 100vh;
  background: var(--bg-page);
  color: var(--text-dark);
}

.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 4px;
  z-index: 9999;
  background: linear-gradient(90deg, var(--primary), #2fb89f);
  transition: width 0.12s ease-out;
}

/* Hero */
.scanner-hero {
  position: relative;
  padding: 112px 0 118px;
  background:
    radial-gradient(circle at 82% 12%, rgba(255, 255, 255, 0.18), transparent 26%),
    linear-gradient(135deg, #0b4d2f 0%, #2f8c59 100%);
  color: white;
  overflow: hidden;
}

.scanner-hero__inner {
  display: grid;
  grid-template-columns: 1fr 0.96fr;
  gap: 72px;
  align-items: center;
}

.back-link {
  display: inline-flex;
  color: rgba(255, 255, 255, 0.86);
  font-weight: 500;
  margin-bottom: 28px;
  transition: transform 0.25s var(--ease-out-quart), color 0.25s ease;
}

.back-link:hover {
  transform: translateX(-4px);
  color: white;
}

.scanner-hero__title {
  font-family: var(--font-serif);
  font-size: clamp(52px, 5.8vw, 82px);
  font-weight: 500;
  line-height: 0.96;
  letter-spacing: -0.04em;
  margin: 0 0 28px;
  max-width: 720px;
}

.scanner-hero__title span {
  font-style: italic;
}

.scanner-hero__text {
  max-width: 650px;
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 20px;
  line-height: 1.55;
}

.scanner-hero__visual {
  position: relative;
  animation: floatImage 5.6s ease-in-out infinite;
}

.scanner-hero__visual::before {
  content: '';
  position: absolute;
  inset: 16px -18px -18px 24px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.13);
  transform: rotate(-3deg);
}

.scanner-hero__image {
  position: relative;
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: var(--radius-xl);
  box-shadow: 0 28px 80px rgba(3, 38, 23, 0.28);
}

@keyframes floatImage {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }

  50% {
    transform: translateY(-12px) rotate(-0.4deg);
  }
}

/* Main cards */
.scanner-content {
  position: relative;
  margin-top: -56px;
  padding-bottom: 72px;
}

.scanner-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.scan-card,
.preview-card,
.result-card {
  border-radius: var(--radius-xl);
  padding: 32px;
  transition: transform 0.35s var(--ease-out-quart), box-shadow 0.35s ease;
}

.scan-card:hover,
.preview-card:hover,
.result-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-hover);
}

.scanner-section-title {
  font-family: var(--font-serif);
  font-size: 30px;
  font-weight: 500;
  margin: 0 0 10px;
}

.scan-card__intro {
  margin: 0 0 28px;
}

.scan-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 28px;
}

.scan-tab {
  border: none;
  border-radius: 999px;
  padding: 14px 18px;
  background: #f5f1ec;
  color: var(--text-body);
  font-weight: 700;
  transition: transform 0.25s var(--ease-out-quart), background 0.25s ease, color 0.25s ease;
}

.scan-tab:hover {
  transform: translateY(-3px);
}

.scan-tab.active {
  background: var(--teal-light);
  color: var(--primary-dark);
}

.scan-steps {
  display: grid;
  gap: 20px;
  list-style: none;
  padding: 0;
  margin: 0 0 30px;
}

.scan-steps li {
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 16px;
  align-items: center;
}

.scan-steps span {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  background: var(--teal-light);
  color: var(--primary-dark);
  display: grid;
  place-items: center;
  font-weight: 800;
}

.scan-steps p {
  margin: 0;
  color: var(--text-body);
  font-size: 16px;
  line-height: 1.45;
}

.phone-scan-box {
  min-height: 250px;
  border: 2px dashed #9aabc4;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  text-align: center;
  gap: 8px;
  padding: 28px;
  margin-bottom: 24px;
  transition: border-color 0.25s ease, background 0.25s ease, transform 0.25s var(--ease-out-quart);
}

.phone-scan-box:hover {
  border-color: var(--primary);
  background: var(--bg-cream);
  transform: scale(1.01);
}

.phone-icon {
  width: 132px;
  height: 132px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  background: var(--teal-light);
  font-size: 34px;
}

.phone-scan-box strong {
  display: block;
  color: var(--text-dark);
}

.phone-scan-box small {
  color: #8b9ab1;
  font-weight: 600;
}

.scanner-form {
  display: grid;
  gap: 14px;
}

.scanner-label {
  color: var(--text-dark);
  font-weight: 800;
}

.scanner-input-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.scanner-input {
  width: 100%;
  min-height: 52px;
  border: 1px solid #d9e0e8;
  border-radius: var(--radius-sm);
  padding: 0 16px;
  color: var(--text-dark);
  font: inherit;
  background: white;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.scanner-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(47, 141, 94, 0.12);
}

.scanner-submit-btn {
  min-height: 52px;
}

.scanner-submit-btn:disabled,
.scanner-demo-btn:disabled {
  cursor: not-allowed;
  opacity: 0.58;
  transform: none;
}

.scanner-file {
  max-width: 260px;
  color: var(--text-body);
}

.scanner-error {
  margin: 14px 0 0;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  background: #fff0ea;
  color: #b63822;
  font-weight: 700;
  line-height: 1.45;
}

.scanner-demo-btn {
  width: 100%;
  justify-content: center;
  font-size: 16px;
}

/* Preview */
.preview-card__eyebrow {
  margin: 0 0 28px;
  color: #465876;
  font-weight: 700;
}

.preview-top {
  display: grid;
  grid-template-columns: 1fr 1.45fr;
  gap: 42px;
  align-items: center;
  margin-bottom: 32px;
}

.mock-phone {
  position: relative;
  width: 108px;
  height: 176px;
  margin: 0 auto;
  border: 3px solid var(--primary);
  border-radius: 8px;
  background: linear-gradient(180deg, #dbf2ed, #f5fbf9);
  display: grid;
  place-items: center;
  transition: transform 0.35s var(--ease-out-quart);
}

.preview-card:hover .mock-phone {
  transform: translateY(-8px) rotate(-1deg);
}

.mock-phone__clip {
  position: absolute;
  top: 0;
  width: 42px;
  height: 30px;
  background: #16a88f;
  border-radius: 0 0 3px 3px;
}

.mock-phone__label {
  width: 72px;
  height: 74px;
  background: white;
  border-radius: 5px;
  display: grid;
  place-content: center;
  gap: 6px;
}

.mock-phone__label span {
  display: block;
  width: 50px;
  height: 5px;
  border-radius: 999px;
  background: #243040;
}

.mock-phone__label span:nth-child(2) {
  background: #e85b3f;
}

.mock-phone__label span:nth-child(3) {
  background: #d08310;
}

.ingredient-note {
  border: 1px solid #e4e2de;
  border-radius: var(--radius-sm);
  padding: 18px 20px;
  min-height: 116px;
  background: white;
}

.ingredient-note strong {
  display: block;
  margin-bottom: 12px;
}

.ingredient-note p {
  margin: 0;
  color: var(--text-body);
  line-height: 1.65;
}

mark {
  border-radius: 4px;
  padding: 2px 5px;
  font-weight: 700;
  background: transparent;
}

mark.danger {
  color: #dc5638;
  background: #ffeae4;
}

mark.warning {
  color: #b87405;
  background: #fff0d5;
}

.camera-preview {
  border-radius: var(--radius-md);
  background: #222a35;
  padding: 28px;
  min-height: 150px;
  display: grid;
  place-items: center;
  margin-bottom: 26px;
}

.camera-frame {
  position: relative;
  width: 170px;
  height: 92px;
  border: 5px solid #2f8d5e;
  border-radius: var(--radius-sm);
  display: grid;
  place-items: center;
}

.camera-frame__box {
  width: 126px;
  height: 56px;
  border: 2px dashed #25c7b2;
  border-radius: 6px;
}

.camera-frame__line {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 2px;
  background: #25c7b2;
}

.preview-caption {
  margin: 0;
  text-align: center;
  color: var(--text-body);
  line-height: 1.5;
}

/* Result */
.scanner-result-section {
  padding: 8px 0 72px;
}

.result-card {
  max-width: 930px;
  margin: 0 auto;
}

.result-card__top {
  display: flex;
  justify-content: space-between;
  gap: 28px;
  border-bottom: 1px solid #e8e4dc;
  padding-bottom: 32px;
  margin-bottom: 32px;
}

.result-eyebrow {
  margin-bottom: 22px;
}

.result-product__main {
  display: flex;
  align-items: center;
  gap: 24px;
}

.product-icon {
  width: 78px;
  height: 78px;
  border-radius: var(--radius-md);
  background: var(--teal-light);
  display: grid;
  place-items: center;
  font-size: 30px;
}

.result-product h2 {
  margin: 0 0 8px;
  font-size: 27px;
}

.result-product p {
  margin: 0;
  font-size: 17px;
}

.score-box {
  text-align: right;
  min-width: 120px;
}

.score-box span,
.score-box small {
  display: block;
  color: #8190aa;
}

.score-box strong {
  display: block;
  color: #c87907;
  font-family: var(--font-serif);
  font-size: 42px;
  font-weight: 500;
  line-height: 1;
}

.safety-meter {
  margin-bottom: 34px;
}

.safety-meter__heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.safety-meter__heading span {
  color: #d17800;
  font-weight: 600;
  max-width: 620px;
  text-align: right;
}

.safety-meter__track {
  height: 14px;
  border-radius: 999px;
  background: #f4f1ec;
  overflow: hidden;
}

.safety-meter__fill {
  width: 45%;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #2f8d5e, #d18a16, #e65b43);
}

.safety-meter__fill.none {
  background: #2f8d5e;
}

.safety-meter__fill.low {
  background: #7fbf61;
}

.safety-meter__fill.medium {
  background: #d18a16;
}

.safety-meter__fill.high {
  background: #e65b43;
}

.trigger-section h3 {
  margin: 0 0 20px;
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 500;
}

.trigger-card {
  display: grid;
  grid-template-columns: 14px 1fr;
  gap: 18px;
  padding: 20px;
  border-radius: var(--radius-sm);
  margin-bottom: 14px;
}

.trigger-card.high {
  background: #fff0ea;
}

.trigger-card.medium {
  background: #fff5df;
}

.trigger-card.low {
  background: #eef8ed;
}

.trigger-dot {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  margin-top: 4px;
  background: #dc5638;
}

.trigger-card.medium .trigger-dot {
  background: #cf7c09;
}

.trigger-card.low .trigger-dot {
  background: #64a84f;
}

.trigger-card strong {
  display: block;
  margin-bottom: 8px;
}

.trigger-card p {
  margin: 0;
  color: var(--text-body);
  line-height: 1.55;
}

.alternative-card {
  margin-top: 32px;
  padding: 28px;
  border-radius: var(--radius-md);
  background: #e7f4ef;
}

.alternative-card h3 {
  font-size: 25px;
  margin: 0 0 12px;
}

.alternative-card p {
  margin: 0 0 22px;
  color: var(--text-body);
  line-height: 1.55;
}

/* Animations */
.reveal {
  opacity: 0;
  transform: translateY(30px);
  animation: revealUp 0.8s var(--ease-out-expo) forwards;
}

.reveal-delay-1 {
  animation-delay: 0.12s;
}

@keyframes revealUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 980px) {
  .scanner-hero {
    padding: 84px 0 104px;
  }

  .scanner-hero__inner,
  .scanner-grid {
    grid-template-columns: 1fr;
  }

  .scanner-hero__inner {
    gap: 44px;
  }

  .scanner-hero__image {
    height: 280px;
  }
}

@media (max-width: 680px) {
  .scanner-hero__title {
    font-size: 50px;
  }

  .scanner-hero__text {
    font-size: 17px;
  }

  .scan-card,
  .preview-card,
  .result-card {
    padding: 24px;
  }

  .scan-tabs,
  .preview-top {
    grid-template-columns: 1fr;
  }

  .result-card__top,
  .result-product__main {
    flex-direction: column;
    align-items: flex-start;
  }

  .score-box {
    text-align: left;
  }
}
</style>
