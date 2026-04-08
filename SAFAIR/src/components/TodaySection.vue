<template>
  <section id="today" class="section today-section">
    <div class="container">
      <div class="today-heading">
        <span class="heart">♡</span>
        <h2>Today in Melbourne</h2>
      </div>

      <div class="risk-banner">
        <div>
          <p class="eyebrow banner-eyebrow">Live Update · 2:30 PM</p>
          <h3>Moderate Asthma Risk</h3>
          <p class="banner-text">
            Some environmental factors may affect your child today. We recommend
            a few simple precautions—especially this afternoon.
          </p>
        </div>

        <div class="warning-icon">⚠</div>
      </div>

      <div class="info-grid">
        <article class="info-card card">
          <div class="image-wrap">
            <img src="../assets/images/air-quality.jpg" alt="Air quality" />
            <span class="image-badge amber">☁</span>
          </div>
          <div class="info-content">
            <h4>Air Quality: Moderate</h4>
            <p>
              Fine particles are elevated. Keep outdoor activities shorter today,
              especially for vigorous exercise.
            </p>
          </div>
        </article>

        <article class="info-card card">
          <div class="image-wrap">
            <img src="../assets/images/pollen.jpeg" alt="Pollen level" />
            <span class="image-badge pink">≋</span>
          </div>
          <div class="info-content">
            <h4>Pollen: High</h4>
            <p>
              Grass pollen is particularly high. Consider keeping windows closed
              between 11am–3pm.
            </p>
          </div>
        </article>
      </div>

      <div class="stats-grid">
        <div class="stat-card mint">
          <span class="stat-label">Temperature</span>
          <strong>18°C</strong>
        </div>

        <div class="stat-card mint">
          <span class="stat-label">Humidity</span>
          <strong>65%</strong>
        </div>

        <div class="stat-card mint">
          <span class="stat-label">Wind</span>
          <strong>Light</strong>
        </div>

        <div class="stat-card uv">
          <span class="stat-label">UV Index</span>
          <strong>6</strong>
        </div>
      </div>

      <div class="action-panel">
        <img
          src="../assets/images/actions-bg.jpeg"
          alt="Background"
          class="action-bg"
        />
        <div class="action-overlay"></div>

        <div class="action-content">
          <h3>What you can do today</h3>

          <ul class="action-list">
            <li>
              <span class="bullet">🏠</span>
              <span>Keep windows closed during peak pollen hours (11am–3pm)</span>
            </li>
            <li>
              <span class="bullet">🧴</span>
              <span>Pack your child's reliever inhaler in their school bag</span>
            </li>
            <li>
              <span class="bullet">🌳</span>
              <span>Choose indoor activities for this afternoon when possible</span>
            </li>
          </ul>

          <button class="btn-pill btn-light">
            See All Recommendations
            <span>→</span>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.today-section {
  background: var(--bg-page);
}

.today-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 22px;
}

.today-heading h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.heart {
  color: #ff6c7d;
  font-size: 22px;
}

.risk-banner {
  background: var(--warning-bg);
  border: 1px solid var(--warning-border);
  border-radius: var(--radius-xl);
  padding: 28px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-bottom: 28px;
  box-shadow: var(--shadow-soft);
}

.banner-eyebrow {
  color: #c66b1f;
  margin: 0 0 10px;
}

.risk-banner h3 {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 600;
}

.banner-text {
  margin: 0;
  max-width: 680px;
  color: var(--text-muted);
  line-height: 1.65;
}

.warning-icon {
  width: 88px;
  height: 88px;
  min-width: 88px;
  border-radius: 50%;
  background: #f5d97b;
  display: grid;
  place-items: center;
  font-size: 34px;
  box-shadow: var(--shadow-soft);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.info-card {
  overflow: hidden;
}

.image-wrap {
  position: relative;
}

.image-wrap img {
  width: 100%;
  height: 250px;
  object-fit: cover;
}

.image-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: white;
  font-size: 16px;
  font-weight: 700;
}

.image-badge.amber {
  background: #ffad0f;
}

.image-badge.pink {
  background: #ff2e7a;
}

.info-content {
  padding: 22px 22px 24px;
}

.info-content h4 {
  margin: 0 0 12px;
  font-size: 18px;
}

.info-content p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  border-radius: 16px;
  padding: 24px 20px;
  text-align: center;
  border: 1px solid rgba(12, 165, 122, 0.16);
}

.stat-card.mint {
  background: #e4f5ee;
}

.stat-card.uv {
  background: var(--uv-bg);
  border-color: rgba(202, 140, 36, 0.18);
}

.stat-label {
  display: block;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #6b7b75;
  margin-bottom: 10px;
  font-weight: 700;
}

.stat-card strong {
  font-size: 30px;
  font-weight: 700;
  color: #117f67;
}

.action-panel {
  position: relative;
  min-height: 340px;
  border-radius: 28px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.action-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.action-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8, 150, 123, 0.92),
    rgba(8, 150, 123, 0.82)
  );
}

.action-content {
  position: relative;
  z-index: 2;
  padding: 34px 32px;
  color: white;
  max-width: 760px;
}

.action-content h3 {
  margin: 0 0 26px;
  font-size: 26px;
  font-weight: 600;
}

.action-list {
  list-style: none;
  padding: 0;
  margin: 0 0 30px;
  display: grid;
  gap: 16px;
}

.action-list li {
  display: flex;
  align-items: center;
  gap: 14px;
  line-height: 1.5;
  font-size: 17px;
}

.bullet {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 12px;
  background: white;
  display: grid;
  place-items: center;
  font-size: 18px;
}

@media (max-width: 992px) {
  .info-grid,
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .risk-banner {
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .today-heading h2 {
    font-size: 24px;
  }

  .risk-banner {
    flex-direction: column;
    align-items: flex-start;
    padding: 24px;
  }

  .warning-icon {
    width: 72px;
    height: 72px;
    min-width: 72px;
    font-size: 28px;
  }

  .info-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .image-wrap img {
    height: 220px;
  }

  .action-panel {
    min-height: auto;
  }

  .action-content {
    padding: 28px 22px;
  }

  .action-content h3 {
    font-size: 24px;
  }

  .action-list li {
    align-items: flex-start;
    font-size: 16px;
  }
}
</style>