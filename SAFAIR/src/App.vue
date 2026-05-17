<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import DisclaimerBanner from './components/DisclaimerBanner.vue'
import HeaderBar from './components/HeaderBar.vue'
import SiteFooter from './components/SiteFooter.vue'

const router  = useRouter()
const breezeWiggle  = ref(false)
const breezeMood    = ref('happy')
const popupOpen     = ref(false)

let wiggleInterval = null
onMounted(() => {
  wiggleInterval = setInterval(() => {
    if (!popupOpen.value) {
      breezeWiggle.value = true
      setTimeout(() => { breezeWiggle.value = false }, 600)
    }
  }, 8000)
  document.addEventListener('click', onOutsideClick)
})
onUnmounted(() => {
  clearInterval(wiggleInterval)
  document.removeEventListener('click', onOutsideClick)
})

function onOutsideClick(e) {
  if (!e.target.closest('.breeze-global')) popupOpen.value = false
}

function onBreezeClick() {
  popupOpen.value = !popupOpen.value
  breezeWiggle.value = true
  setTimeout(() => { breezeWiggle.value = false }, 600)
}

function quickAction(action) {
  popupOpen.value = false
  if (action === 'dustwatch') router.push({ path: '/assistance', query: { tab: 'dustwatch' } })
  else if (action === 'safespots') router.push({ path: '/assistance', query: { tab: 'safespots' } })
  else if (action === 'scanner') router.push('/housing-scanner')
}
</script>

<template>
  <HeaderBar />
  <router-view />
  <DisclaimerBanner />
  <SiteFooter />

  <!-- ── Global Breeze mascot — fixed bottom-right ── -->
  <div class="breeze-global" :class="{ wiggle: breezeWiggle }">

    <!-- Quick-action popup -->
    <transition name="popup-fade">
      <div v-if="popupOpen" class="breeze-popup">
        <p class="popup-greeting">
          <span v-if="breezeMood === 'happy'">Hi! What can I help with?</span>
          <span v-else-if="breezeMood === 'curious'">Let me help you stay safe!</span>
          <span v-else>Better check the air today!</span>
        </p>

        <button class="popup-btn" @click="quickAction('dustwatch')">
          <strong>Check dust levels</strong>
          <small>See construction sites nearby</small>
        </button>

        <button class="popup-btn" @click="quickAction('safespots')">
          <strong>Find safe spots</strong>
          <small>Parks with clean air near you</small>
        </button>

        <button class="popup-btn" @click="quickAction('scanner')">
          <strong>Scan a product</strong>
          <small>Check household ingredients</small>
        </button>

        <div class="popup-arrow"></div>
      </div>
    </transition>

    <!-- Mascot -->
    <div class="breeze-mascot-wrap" @click="onBreezeClick" role="button" :aria-expanded="popupOpen" aria-label="Breeze assistant" tabindex="0">
      <!-- Happy mood -->
      <svg v-if="breezeMood === 'happy'" class="breeze-svg" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
        <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
        <circle cx="60" cy="72" r="46" fill="none" stroke="#0d9488" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring"/>
        <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
        <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
        <ellipse cx="47" cy="79" rx="7" ry="4.5" fill="#0d9488" opacity=".2"/>
        <ellipse cx="73" cy="79" rx="7" ry="4.5" fill="#0d9488" opacity=".2"/>
        <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
        <circle cx="52" cy="67" r="3.8" fill="#1c1917"/><circle cx="70" cy="67" r="3.8" fill="#1c1917"/>
        <circle cx="53.5" cy="65.5" r="1.4" fill="white"/><circle cx="71.5" cy="65.5" r="1.4" fill="white"/>
        <path d="M49 81 Q60 91 71 81" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
        <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".85"/>
        <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".85"/>
        <circle cx="94" cy="45" r="2.5" fill="#0d9488" opacity=".7"/>
      </svg>
      <!-- Curious mood -->
      <svg v-else-if="breezeMood === 'curious'" class="breeze-svg" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
        <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
        <circle cx="60" cy="72" r="46" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring"/>
        <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
        <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
        <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
        <circle cx="53" cy="64" r="3.8" fill="#1c1917"/><circle cx="71" cy="64" r="3.8" fill="#1c1917"/>
        <circle cx="54.5" cy="62.5" r="1.4" fill="white"/><circle cx="72.5" cy="62.5" r="1.4" fill="white"/>
        <ellipse cx="60" cy="84" rx="4.5" ry="3" fill="#c2410c" opacity=".45"/>
        <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".75"/>
        <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".8"/>
      </svg>
      <!-- Worried mood -->
      <svg v-else class="breeze-svg" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
        <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
        <circle cx="60" cy="72" r="46" fill="none" stroke="#ea2951" stroke-width="2.5" stroke-dasharray="4 3" opacity=".5" class="breeze-ring"/>
        <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
        <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
        <ellipse cx="47" cy="79" rx="7" ry="4.5" fill="#ea2951" opacity=".22"/>
        <ellipse cx="73" cy="79" rx="7" ry="4.5" fill="#ea2951" opacity=".22"/>
        <path d="M46 57 Q52 53 58 57" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
        <path d="M62 57 Q68 53 74 57" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
        <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
        <circle cx="51" cy="67" r="3.8" fill="#1c1917"/><circle cx="69" cy="67" r="3.8" fill="#1c1917"/>
        <circle cx="52.5" cy="65.5" r="1.4" fill="white"/><circle cx="70.5" cy="65.5" r="1.4" fill="white"/>
        <path d="M49 85 Q60 79 71 85" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
        <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".65"/>
        <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".65"/>
      </svg>
    </div>
  </div>
</template>

<style>
/* ── Breeze global ──────────────────────────────────────────── */
.breeze-global {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 500;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  user-select: none;
}

.breeze-mascot-wrap {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.breeze-svg {
  width: 88px;
  height: auto;
  filter: drop-shadow(0 10px 24px rgba(251,146,60,0.35)) drop-shadow(0 2px 6px rgba(0,0,0,0.12));
  animation: global-float 4s ease-in-out infinite;
  transition: filter 0.2s ease;
}

.breeze-mascot-wrap:hover .breeze-svg {
  filter: drop-shadow(0 16px 32px rgba(251,146,60,0.5)) drop-shadow(0 4px 10px rgba(0,0,0,0.15));
  transform: scale(1.08);
}

.breeze-mascot-wrap:active .breeze-svg { transform: scale(0.92); }

@keyframes global-float {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-9px); }
}

@keyframes global-wiggle {
  0%  { transform: rotate(0deg); }
  20% { transform: rotate(-14deg) scale(1.12); }
  40% { transform: rotate(12deg) scale(1.16); }
  60% { transform: rotate(-8deg) scale(1.1); }
  80% { transform: rotate(5deg); }
  100%{ transform: rotate(0deg); }
}

.breeze-global.wiggle .breeze-svg {
  animation: global-wiggle 0.6s ease, global-float 4s ease-in-out 0.6s infinite;
}

@keyframes breeze-ring-spin {
  0%   { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -60; }
}
.breeze-global .breeze-ring { animation: breeze-ring-spin 4s linear infinite; }

/* ── Popup ──────────────────────────────────────────────────── */
.breeze-popup {
  background: white;
  border-radius: 20px;
  padding: 16px;
  width: 240px;
  box-shadow: 0 20px 60px rgba(10,30,20,0.18), 0 4px 16px rgba(10,30,20,0.1);
  border: 1px solid rgba(10,40,30,0.08);
  position: relative;
}

.popup-greeting {
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 12px;
  font-family: var(--font-sans, Inter, sans-serif);
}

.popup-btn {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  background: #fafaf8;
  border: 1.5px solid rgba(10,40,30,0.07);
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  text-align: left;
  margin-bottom: 7px;
  transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
  font-family: var(--font-sans, Inter, sans-serif);
}
.popup-btn:last-of-type { margin-bottom: 0; }
.popup-btn:hover {
  background: white;
  border-color: rgba(13,107,94,0.25);
  transform: translateX(-3px);
}
.popup-btn strong {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
}
.popup-btn small {
  font-size: 11px;
  color: #8a9ab0;
  line-height: 1.3;
}

.popup-arrow {
  position: absolute;
  bottom: -8px;
  right: 40px;
  width: 16px;
  height: 16px;
  background: white;
  border-right: 1px solid rgba(10,40,30,0.08);
  border-bottom: 1px solid rgba(10,40,30,0.08);
  transform: rotate(45deg);
}

/* Popup transition */
.popup-fade-enter-active { transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.16,1,0.3,1); }
.popup-fade-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.popup-fade-enter-from  { opacity: 0; transform: translateY(10px) scale(0.95); }
.popup-fade-leave-to    { opacity: 0; transform: translateY(6px) scale(0.97); }

@media (max-width: 480px) {
  .breeze-global { bottom: 16px; right: 16px; }
  .breeze-svg { width: 70px; }
  .breeze-popup { width: 210px; }
}
</style>