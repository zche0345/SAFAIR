<template>
  <header class="app-navbar">
    <div class="container navbar-inner">

      <!-- Brand -->
      <router-link to="/" class="navbar-brand">
        <img src="../assets/images/logo.svg" alt="BRTHEZ" class="brand-logo" />
        <span class="brand-name">BRTHEZ</span>
      </router-link>

      <!-- Nav -->
      <nav class="navbar-links">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/insights" class="nav-link">Insights</router-link>

        <!-- Assistance dropdown -->
        <div
          class="nav-dropdown"
          @mouseenter="dropdownOpen = true"
          @mouseleave="dropdownOpen = false"
        >
          <button
            class="nav-link nav-btn"
            :class="{ 'router-link-active': isAssistanceActive }"
            @click="dropdownOpen = !dropdownOpen"
          >
            Assistance
            <svg
              class="chevron"
              :class="{ open: dropdownOpen }"
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>

          <transition name="drop">
            <div v-if="dropdownOpen" class="dropdown-panel">
              <router-link
                v-for="item in assistanceItems"
                :key="item.to"
                :to="item.to"
                class="dropdown-item"
                @click="dropdownOpen = false"
              >
                <p class="dropdown-title">{{ item.title }}</p>
                <p class="dropdown-desc">{{ item.desc }}</p>
              </router-link>
            </div>
          </transition>
        </div>

        <router-link to="/asthma-learn" class="nav-link">Learn</router-link>
      </nav>

    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const dropdownOpen = ref(false)
const route = useRoute()

const assistanceItems = [
  {
    to: '/construction-dust',
    title: 'Construction Dust Alerts',
    desc: 'Track building sites near you',
  },
  {
    to: '/safe-route-planning',
    title: 'Safer Route Planner',
    desc: 'Avoid triggers on your route',
  },
  {
    to: '/housing-scanner',
    title: 'Product Scanner',
    desc: 'Check household products',
  },
]

const isAssistanceActive = computed(() =>
  ['/construction-dust'].includes(route.path)
)
</script>

<style scoped>
.app-navbar {
  background: #ffffff;
  border-bottom: 1px solid #eceae5;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-inner {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

/* ── Brand ──────────────────────────────── */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 11px;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-logo {
  width: 38px;
  height: 38px;
  display: block;
  flex-shrink: 0;
}




.brand-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-dark);
  letter-spacing: 0.02em;
}

/* ── Nav ────────────────────────────────── */
.navbar-links {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  text-decoration: none;
  color: var(--text-body);
  font-size: 15px;
  font-weight: 500;
  padding: 9px 18px;
  border-radius: 999px;
  transition: background 0.18s ease, color 0.18s ease;
  white-space: nowrap;
}

.nav-link:hover {
  background: #f2efea;
  color: var(--text-dark);
}

.nav-link.router-link-active {
  background: #e8f4f1;
  color: var(--primary-dark);
}

/* ── Dropdown trigger button ────────────── */
.nav-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font-sans);
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.chevron {
  transition: transform 0.2s ease;
  opacity: 0.55;
}

.chevron.open {
  transform: rotate(180deg);
  opacity: 0.9;
}

/* ── Dropdown panel ─────────────────────── */
.nav-dropdown {
  position: relative;
}

.dropdown-panel {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  background: white;
  border-radius: 16px;
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.04),
    0 12px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.06);
  padding: 8px;
  min-width: 260px;
  z-index: 200;
}

.dropdown-item {
  display: block;
  padding: 14px 18px;
  border-radius: 10px;
  text-decoration: none;
  transition: background 0.15s ease;
}

.dropdown-item:hover {
  background: #f5f3ef;
}

.dropdown-title {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-dark);
  line-height: 1.2;
}

.dropdown-desc {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.3;
}

/* ── Transition ─────────────────────────── */
.drop-enter-active,
.drop-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.drop-enter-from,
.drop-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── Responsive ─────────────────────────── */
@media (max-width: 992px) {
  .navbar-inner {
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .navbar-inner {
    height: auto;
    flex-wrap: wrap;
    padding: 14px 0;
    gap: 12px;
  }

  .navbar-links {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .dropdown-panel {
    right: auto;
    left: 0;
  }
}
</style>