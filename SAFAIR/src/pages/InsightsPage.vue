<template>
  <div class="insights-page">
    <section class="insights-hero">
      <div class="container">
        <div class="brand-row">
          <div class="brand-left">
            <div class="brand-icon">✦</div>
            <span class="brand-name">SAFAIR</span>
            <router-link to="/" class="back-link">‹ Back to Home</router-link>
          </div>
        </div>

        <div class="hero-copy">
          <h1>What's in Melbourne's air today?</h1>
          <p>Let's understand the conditions affecting your child</p>
        </div>
      </div>
    </section>

    <section class="section insights-content">
      <div class="container">
        <div class="summary-card">
          <div class="summary-icon">⚠</div>
          <div class="summary-text">
            <h2>Moderate Risk Today</h2>
            <p>
              A few environmental factors are elevated today. Here's what you
              should know and simple steps to keep your child comfortable and safe.
            </p>
          </div>
        </div>

        <div class="section-heading">
          <span class="heart">♡</span>
          <h2>The factors at play</h2>
        </div>

        <div class="factors-list">
          <article
            v-for="factor in factors"
            :key="factor.title"
            class="factor-card"
            :class="factor.theme"
          >
            <div class="factor-left">
              <div class="factor-icon" :class="factor.theme">
                {{ factor.icon }}
              </div>

              <div class="factor-content">
                <div class="factor-top">
                  <h3>{{ factor.title }}</h3>
                  <span class="factor-badge" :class="factor.theme">
                    {{ factor.value }}
                  </span>
                </div>

                <p class="factor-description">
                  {{ factor.description }}
                </p>

                <p class="factor-note">
                  {{ factor.note }}
                </p>

                <button
                  class="factor-toggle"
                  @click="toggleFactor(factor.title)"
                >
                  Why does this matter?
                  <span
                    class="arrow"
                    :class="{ open: openFactor === factor.title }"
                  >
                    ˅
                  </span>
                </button>

                <transition name="fade">
                  <div
                    v-if="openFactor === factor.title"
                    class="factor-extra"
                  >
                    {{ factor.explanation }}
                  </div>
                </transition>
              </div>
            </div>
          </article>
        </div>

        <div class="action-banner">
          <img
            src="../assets/images/insights-action-bg.jpg"
            alt="Family outdoors"
            class="action-banner-bg"
          />
          <div class="action-banner-overlay"></div>

          <div class="action-banner-content">
            <h2>Ready for action?</h2>
            <p>
              Now that you know what's happening in the air, let's talk about
              practical steps you can take today to keep your child safe and
              comfortable.
            </p>

            <router-link to="/" class="btn-pill btn-light action-link">
              See What You Can Do
              <span>→</span>
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const openFactor = ref(null)

const toggleFactor = (title) => {
  openFactor.value = openFactor.value === title ? null : title
}

const factors = [
  {
    title: 'Air Quality',
    icon: '☁',
    value: 'Moderate',
    description: 'Fine particles in the air are at moderate levels today',
    note: 'May cause mild symptoms during outdoor exercise',
    explanation:
      'Air quality matters because airborne particles can irritate sensitive lungs and make breathing less comfortable, especially during outdoor activity.',
    theme: 'amber',
  },
  {
    title: 'Pollen Count',
    icon: '≋',
    value: 'High',
    description: 'Grass pollen is particularly high today',
    note: 'Most likely to trigger symptoms, especially 11am–3pm',
    explanation:
      'High pollen can trigger asthma symptoms in children who are sensitive to allergens. Midday and early afternoon are often the worst times.',
    theme: 'pink',
  },
  {
    title: 'Temperature',
    icon: '◔',
    value: '18°C',
    description: 'Cool, stable conditions',
    note: 'Stable conditions are ideal—no concerns here',
    explanation:
      'Stable temperature is usually easier on breathing and does not add extra strain the way extreme or rapidly changing weather sometimes can.',
    theme: 'mint',
  },
  {
    title: 'Humidity',
    icon: '◍',
    value: '65%',
    description: 'Comfortable moisture levels',
    note: 'Humidity is in the ideal range',
    explanation:
      'Balanced humidity can feel more comfortable for breathing. Very dry or very humid conditions can sometimes make symptoms worse.',
    theme: 'mint',
  },
  {
    title: 'UV Index',
    icon: '☼',
    value: '6 (High)',
    description: 'Sun protection recommended',
    note: 'Remember sunscreen if they go outside',
    explanation:
      'UV does not directly cause asthma, but it still matters when planning outdoor time. Higher UV means extra sun protection is needed.',
    theme: 'amber',
  },
]
</script>

<style scoped>
.insights-page {
  background: var(--bg-page);
  min-height: 100vh;
}

.insights-hero {
  background: linear-gradient(135deg, var(--primary-teal), var(--primary));
  padding: 56px 0 72px;
}

.brand-row {
  margin-bottom: 44px;
}

.brand-left {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.18);
  display: grid;
  place-items: center;
  font-size: 15px;
}

.brand-name {
  font-size: 18px;
  font-weight: 500;
}

.back-link {
  color: rgba(255, 255, 255, 0.92);
  font-size: 18px;
}

.hero-copy h1 {
  margin: 0 0 20px;
  max-width: 700px;
  font-size: 72px;
  line-height: 1.02;
  font-weight: 400;
  color: white;
}

.hero-copy p {
  margin: 0;
  font-size: 22px;
  color: rgba(255, 255, 255, 0.92);
}

.insights-content {
  padding-top: 56px;
}

.summary-card {
  background: rgba(248, 242, 229, 0.72);
  border: 1px solid #eddca7;
  border-radius: 28px;
  padding: 38px 42px;
  display: flex;
  align-items: center;
  gap: 28px;
  box-shadow: var(--shadow-soft);
  margin-bottom: 64px;
}

.summary-icon {
  width: 100px;
  height: 100px;
  min-width: 100px;
  border-radius: 50%;
  background: #f5d97b;
  display: grid;
  place-items: center;
  font-size: 42px;
  box-shadow: var(--shadow-soft);
}

.summary-text h2 {
  margin: 0 0 14px;
  font-size: 36px;
  font-weight: 500;
}

.summary-text p {
  margin: 0;
  font-size: 18px;
  line-height: 1.7;
  color: var(--text-muted);
  max-width: 900px;
}

.section-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 26px;
}

.section-heading h2 {
  margin: 0;
  font-size: 32px;
  font-weight: 500;
}

.heart {
  color: #ff6c7d;
  font-size: 24px;
}

.factors-list {
  display: grid;
  gap: 24px;
  margin-bottom: 56px;
}

.factor-card {
  background: white;
  border-radius: 28px;
  box-shadow: var(--shadow-soft);
  padding: 40px;
}

.factor-card.mint {
  border: 1px solid rgba(55, 214, 176, 0.28);
}

.factor-left {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}

.factor-icon {
  width: 64px;
  height: 64px;
  min-width: 64px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  font-size: 28px;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08);
}

.factor-icon.amber {
  background: #f4e4b9;
  color: #c96a14;
}

.factor-icon.pink {
  background: #f6dde3;
  color: #ef2f73;
}

.factor-icon.mint {
  background: #d8f4e9;
  color: #138067;
}

.factor-content {
  flex: 1;
  min-width: 0;
}

.factor-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.factor-top h3 {
  margin: 0;
  font-size: 28px;
  font-weight: 500;
}

.factor-badge {
  border-radius: 999px;
  padding: 12px 22px;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.factor-badge.amber {
  background: #fbf2dd;
  color: #cf7016;
  border: 1px solid #edd18e;
}

.factor-badge.pink {
  background: #fde7ee;
  color: #eb2c73;
  border: 1px solid #f5c7d5;
}

.factor-badge.mint {
  background: #e4f7ef;
  color: #138067;
  border: 1px solid #b7ead6;
}

.factor-description {
  margin: 0 0 14px;
  font-size: 18px;
  color: #485465;
}

.factor-note {
  margin: 0 0 20px;
  font-size: 17px;
  color: #7b8494;
  font-style: italic;
}

.factor-toggle {
  border: none;
  background: transparent;
  padding: 0;
  color: #00958f;
  font-size: 17px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.arrow {
  transition: transform 0.2s ease;
}

.arrow.open {
  transform: rotate(180deg);
}

.factor-extra {
  margin-top: 16px;
  color: var(--text-muted);
  line-height: 1.7;
  max-width: 900px;
}

.action-banner {
  position: relative;
  min-height: 360px;
  border-radius: 30px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.action-banner-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.action-banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8, 150, 123, 0.88),
    rgba(8, 150, 123, 0.72)
  );
}

.action-banner-content {
  position: relative;
  z-index: 2;
  color: white;
  max-width: 720px;
  padding: 56px 48px;
}

.action-banner-content h2 {
  margin: 0 0 18px;
  font-size: 36px;
  font-weight: 500;
}

.action-banner-content p {
  margin: 0 0 34px;
  font-size: 18px;
  line-height: 1.7;
}

.action-link {
  display: inline-flex;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 992px) {
  .hero-copy h1 {
    font-size: 54px;
  }

  .summary-card,
  .factor-card {
    padding: 28px;
  }

  .summary-text h2 {
    font-size: 30px;
  }
}

@media (max-width: 768px) {
  .insights-hero {
    padding: 40px 0 56px;
  }

  .brand-left {
    flex-wrap: wrap;
  }

  .hero-copy h1 {
    font-size: 40px;
    max-width: 100%;
  }

  .hero-copy p {
    font-size: 18px;
  }

  .summary-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
    margin-bottom: 48px;
  }

  .summary-icon {
    width: 82px;
    height: 82px;
    min-width: 82px;
    font-size: 34px;
  }

  .summary-text h2 {
    font-size: 28px;
  }

  .section-heading h2 {
    font-size: 24px;
  }

  .factor-left {
    flex-direction: column;
    gap: 20px;
  }

  .factor-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .factor-top h3 {
    font-size: 24px;
  }

  .action-banner-content {
    padding: 34px 24px;
  }

  .action-banner-content h2 {
    font-size: 28px;
  }

  .action-banner-content p {
    font-size: 16px;
  }
}
</style>