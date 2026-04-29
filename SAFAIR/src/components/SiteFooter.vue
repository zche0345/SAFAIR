<template>
  <footer class="site-footer">
    <div class="container footer-inner">

      <div class="footer-brand-col">
        <div class="footer-brand">
          <div class="footer-brand-icon">+</div>
          <span class="footer-brand-name">BRTHEZ</span>
        </div>
        <p class="footer-tagline">Clear air. Better days.</p>
        <p class="footer-desc">
          Real-time air quality insights for Melbourne families. Helping
          parents make confident decisions about outdoor activities.
        </p>
      </div>

      <div class="footer-links-col">
        <p class="footer-col-heading">Tools</p>
        <nav class="footer-nav">
          <router-link to="/insights" class="footer-link">Air Quality Insights</router-link>
          <router-link to="/construction-dust" class="footer-link">Construction Dust Alerts</router-link>
          <router-link to="/recommendations" class="footer-link">Recommendations</router-link>
        </nav>
      </div>

      <div class="footer-links-col">
        <p class="footer-col-heading">Learn</p>
        <nav class="footer-nav">
          <a href="#" class="footer-link">About Asthma Triggers</a>
          <a href="#" class="footer-link">Understanding Air Quality</a>
          <a href="#" class="footer-link">Melbourne Air Data</a>
          <a href="#" class="footer-link">EPA Victoria</a>
        </nav>
      </div>

      <div class="footer-links-col">
        <p class="footer-col-heading">Support</p>
        <nav class="footer-nav">
          <a href="#" class="footer-link">How It Works</a>
          <a href="#" class="footer-link">Privacy Policy</a>
          <a href="#" class="footer-link">Terms of Use</a>
          <a href="#" class="footer-link">Contact Us</a>
        </nav>
      </div>

    </div>

    <div class="footer-bottom">
      <div class="container footer-bottom-inner">
        <p class="footer-legal">
          © 2025 BRTHEZ. Environmental data sourced from EPA Victoria and local
          government records. Not a substitute for medical advice.
        </p>
        <div class="footer-disclaimer-badge">
          <span class="footer-disclaimer-dot"></span>
          Data updated live
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
// No props needed — footer is purely static
</script>

<style scoped>
.site-footer {
  background: var(--text-dark);
  font-family: var(--font-sans);
}

.footer-inner {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr 1fr;
  gap: 56px;
  padding: 72px 0 56px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

/* ── Brand col ──────────────────────────── */
.footer-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.footer-brand-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: grid;
  place-items: center;
  font-size: 20px;
  font-weight: 300;
  line-height: 1;
  flex-shrink: 0;
}

.footer-brand-name {
  font-size: 18px;
  font-weight: 700;
  color: white;
  letter-spacing: 0.04em;
}

.footer-tagline {
  margin: 0 0 14px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.35);
}

.footer-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.46);
  max-width: 280px;
}

/* ── Link cols ──────────────────────────── */
.footer-col-heading {
  margin: 0 0 18px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.35);
}

.footer-nav {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-link {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: color 0.18s ease;
  line-height: 1.4;
}

.footer-link:hover {
  color: white;
}

/* ── Bottom bar ─────────────────────────── */
.footer-bottom {
  padding: 22px 0;
}

.footer-bottom-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.footer-legal {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.28);
  line-height: 1.6;
  max-width: 680px;
}

.footer-disclaimer-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.38);
  white-space: nowrap;
}

.footer-disclaimer-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #3bbfaa;
  animation: pulse-dot 2.4s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(0.8); }
}

/* ── Responsive ─────────────────────────── */
@media (max-width: 992px) {
  .footer-inner {
    grid-template-columns: 1fr 1fr;
    gap: 40px;
  }

  .footer-brand-col {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .footer-inner {
    gap: 32px;
    padding: 52px 0 40px;
  }

  .footer-bottom-inner {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .footer-inner {
    grid-template-columns: 1fr;
  }
}
</style>