<template>
  <div class="construction-page">
    <section class="dust-hero">
      <div class="container">
        <div class="hero-top">
          <div class="hero-brand">
            <div class="hero-brand-icon">✦</div>
            <span class="hero-brand-name">SAFAIR</span>
            <router-link to="/" class="hero-back-link">‹ Back to Home</router-link>
          </div>
        </div>

        <div class="hero-copy">
          <h1>Construction Dust in Your Area</h1>
          <p>
            Understanding nearby building work and how it might affect your child
          </p>
        </div>
      </div>
    </section>

    <section class="section dust-content">
      <div class="container">
        <div class="suburb-card card">
          <h2>Choose your suburb</h2>
          <p>
            Select your Melbourne suburb to see construction activity and dust risk
            specific to your area
          </p>

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
            <span class="updated-dot">◔</span>
            <span>Last updated: {{ activeArea.lastUpdated }}</span>
          </div>
        </div>

        <div class="risk-summary-card">
          <img
            src="../assets/images/construction-summary-bg.jpg"
            alt="Construction site"
            class="risk-summary-bg"
          />
          <div class="risk-summary-overlay"></div>

          <div class="risk-summary-content">
            <div class="risk-summary-icon">🚧</div>

            <div>
              <p class="risk-summary-tag">
                HIGH DUST RISK IN {{ selectedSuburb.toUpperCase() }}
              </p>
              <h2>{{ activeArea.activeSites.length }} active construction sites nearby</h2>
              <p class="risk-summary-text">
                Wind is currently carrying dust particles toward your area. We
                recommend extra precautions today to keep your child comfortable.
              </p>
            </div>
          </div>
        </div>

        <div class="sites-section">
          <h2>Active construction sites</h2>

          <div class="site-list">
            <article
              v-for="site in activeArea.activeSites"
              :key="site.name"
              class="site-card"
              :class="site.riskClass"
            >
              <div class="site-copy">
                <h3>{{ site.name }}</h3>
                <p class="site-type">{{ site.type }}</p>
                <p class="site-distance">📍 {{ site.distance }}</p>
              </div>

              <span class="site-badge" :class="site.riskClass">
                {{ site.riskLabel }}
              </span>
            </article>
          </div>
        </div>

        <div class="dust-actions-panel">
          <img
            src="../assets/images/actions-bg.jpeg"
            alt="Background"
            class="dust-actions-bg"
          />
          <div class="dust-actions-overlay"></div>

          <div class="dust-actions-content">
            <h2>What you can do today</h2>

            <ul class="dust-actions-list">
              <li v-for="(tip, index) in activeArea.tips" :key="`${tip}-${index}`">
                {{ tip }}
              </li>
            </ul>

            <router-link to="/recommendations" class="dust-actions-btn">
              See Full Action Plan
              <span>→</span>
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const dustData = {
  Carlton: {
    lastUpdated: '6:29 am',
    windDirection: 'NE',
    activeSites: [
      {
        name: 'Smith Street Development',
        type: 'Demolition & excavation',
        distance: '2 blocks from your location',
        riskLabel: 'High Risk',
        riskClass: 'high',
      },
      {
        name: 'Victoria Street Apartments',
        type: 'Concrete work',
        distance: '5 blocks from your location',
        riskLabel: 'Moderate Risk',
        riskClass: 'moderate',
      },
      {
        name: 'Johnston Street Renovation',
        type: 'Interior fit-out',
        distance: '8 blocks from your location',
        riskLabel: 'Low Risk',
        riskClass: 'low',
      },
    ],
    tips: [
      'Keep windows and doors closed to prevent dust entering your home',
      'Choose indoor activities, especially this afternoon',
      'Avoid walking near Smith Street where dust levels are highest',
      "Have your child's reliever inhaler ready and accessible",
    ],
  },

  Fitzroy: {
    lastUpdated: '6:31 am',
    windDirection: 'E',
    activeSites: [
      {
        name: 'Brunswick Street Works',
        type: 'Road resurfacing',
        distance: '3 blocks from your location',
        riskLabel: 'Moderate Risk',
        riskClass: 'moderate',
      },
      {
        name: 'Napier Lane Redevelopment',
        type: 'Facade works',
        distance: '6 blocks from your location',
        riskLabel: 'Low Risk',
        riskClass: 'low',
      },
    ],
    tips: [
      'Keep outdoor play shorter today',
      'Prefer side streets away from active building zones',
      'Wash hands and face after coming home',
      'Keep asthma medication easy to access',
    ],
  },

  Richmond: {
    lastUpdated: '6:25 am',
    windDirection: 'ENE',
    activeSites: [
      {
        name: 'Bridge Road Tower Project',
        type: 'Excavation',
        distance: '2 blocks from your location',
        riskLabel: 'High Risk',
        riskClass: 'high',
      },
      {
        name: 'Swan Street Upgrade',
        type: 'Road work',
        distance: '4 blocks from your location',
        riskLabel: 'Moderate Risk',
        riskClass: 'moderate',
      },
    ],
    tips: [
      'Avoid the highest-risk streets this morning',
      'Use indoor options for active play',
      'Keep doors and windows closed during windy periods',
      'Watch for coughing or wheezing after outdoor exposure',
    ],
  },

  'South Yarra': {
    lastUpdated: '6:27 am',
    windDirection: 'NNE',
    activeSites: [
      {
        name: 'Toorak Road Development',
        type: 'Concrete drilling',
        distance: '4 blocks from your location',
        riskLabel: 'Moderate Risk',
        riskClass: 'moderate',
      },
      {
        name: 'Commercial Tower Upgrade',
        type: 'Internal fit-out',
        distance: '7 blocks from your location',
        riskLabel: 'Low Risk',
        riskClass: 'low',
      },
    ],
    tips: [
      'Plan outside time for quieter hours',
      'Avoid lingering near fenced construction zones',
      'Keep your child hydrated and comfortable',
      'Carry the reliever inhaler when heading out',
    ],
  },

  'St Kilda': {
    lastUpdated: '6:18 am',
    windDirection: 'SE',
    activeSites: [
      {
        name: 'Marine Parade Upgrade',
        type: 'Footpath and road works',
        distance: '5 blocks from your location',
        riskLabel: 'Moderate Risk',
        riskClass: 'moderate',
      },
    ],
    tips: [
      'Choose less dusty walking routes',
      'Keep an eye on symptoms after windy outdoor time',
      'Change clothes after long outdoor exposure',
      'Use normal asthma precautions through the day',
    ],
  },

  Brunswick: {
    lastUpdated: '6:22 am',
    windDirection: 'N',
    activeSites: [
      {
        name: 'Sydney Road Redevelopment',
        type: 'Demolition',
        distance: '3 blocks from your location',
        riskLabel: 'High Risk',
        riskClass: 'high',
      },
      {
        name: 'Albert Street Build',
        type: 'Excavation',
        distance: '6 blocks from your location',
        riskLabel: 'Moderate Risk',
        riskClass: 'moderate',
      },
    ],
    tips: [
      'Reduce outdoor time around lunch and afternoon',
      'Prefer indoor activities for today',
      'Keep home ventilation controlled',
      'Monitor for early breathing discomfort',
    ],
  },

  Collingwood: {
    lastUpdated: '6:20 am',
    windDirection: 'NW',
    activeSites: [
      {
        name: 'Warehouse Conversion Project',
        type: 'Structural work',
        distance: '2 blocks from your location',
        riskLabel: 'High Risk',
        riskClass: 'high',
      },
      {
        name: 'Oxford Street Upgrades',
        type: 'Utility works',
        distance: '5 blocks from your location',
        riskLabel: 'Low Risk',
        riskClass: 'low',
      },
    ],
    tips: [
      'Avoid areas closest to the warehouse conversion site',
      'Keep rescue medication nearby',
      'Short indoor activities are the safer option today',
      'Close windows during wind gusts',
    ],
  },

  Prahran: {
    lastUpdated: '6:16 am',
    windDirection: 'ESE',
    activeSites: [
      {
        name: 'Chapel Street Apartment Build',
        type: 'Exterior works',
        distance: '4 blocks from your location',
        riskLabel: 'Moderate Risk',
        riskClass: 'moderate',
      },
    ],
    tips: [
      'Keep routines gentle today',
      'Avoid spending too long near active work sites',
      'Use indoor breaks between outings',
      'Be ready for symptoms if your child is sensitive',
    ],
  },

  Footscray: {
    lastUpdated: '6:12 am',
    windDirection: 'W',
    activeSites: [
      {
        name: 'Station Precinct Works',
        type: 'Bulk excavation',
        distance: '2 blocks from your location',
        riskLabel: 'High Risk',
        riskClass: 'high',
      },
      {
        name: 'Residential Build Site',
        type: 'Concrete pumping',
        distance: '5 blocks from your location',
        riskLabel: 'Moderate Risk',
        riskClass: 'moderate',
      },
    ],
    tips: [
      'Prefer indoor spaces this afternoon',
      'Avoid the station precinct if possible',
      'Shower and change after longer outdoor exposure',
      'Keep inhaler access simple and immediate',
    ],
  },

  Hawthorn: {
    lastUpdated: '6:14 am',
    windDirection: 'NE',
    activeSites: [
      {
        name: 'Riversdale Road Works',
        type: 'Road excavation',
        distance: '6 blocks from your location',
        riskLabel: 'Low Risk',
        riskClass: 'low',
      },
    ],
    tips: [
      'Today looks relatively manageable',
      'Normal routines are mostly okay with awareness',
      'Avoid any visibly dusty streets if passing by',
      'Carry medication as usual',
    ],
  },
}

const suburbs = Object.keys(dustData)
const selectedSuburb = ref('Carlton')

const activeArea = computed(() => dustData[selectedSuburb.value])

const selectSuburb = (suburb) => {
  selectedSuburb.value = suburb
}
</script>

<style scoped>
.construction-page {
  background: var(--bg-page);
  min-height: 100vh;
}

.dust-hero {
  background: linear-gradient(135deg, #f0627e, #d87a46);
  padding: 56px 0 76px;
}

.hero-top {
  margin-bottom: 48px;
}

.hero-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
}

.hero-brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.92);
  color: #eb5a73;
  display: grid;
  place-items: center;
  font-size: 16px;
}

.hero-brand-name {
  font-size: 18px;
  font-weight: 500;
}

.hero-back-link {
  color: rgba(255, 255, 255, 0.94);
  font-size: 18px;
}

.hero-copy h1 {
  margin: 0 0 20px;
  max-width: 560px;
  font-size: 72px;
  line-height: 1.02;
  font-weight: 400;
  color: white;
}

.hero-copy p {
  margin: 0;
  max-width: 640px;
  font-size: 22px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.94);
}

.dust-content {
  padding-top: 42px;
}

.suburb-card {
  padding: 42px 44px;
  margin-bottom: 46px;
}

.suburb-card h2,
.sites-section h2 {
  margin: 0 0 14px;
  font-size: 34px;
  font-weight: 500;
  color: var(--text-dark);
}

.suburb-card p {
  margin: 0 0 28px;
  color: var(--text-muted);
  font-size: 18px;
  line-height: 1.6;
}

.suburb-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 30px;
}

.suburb-pill {
  border: 1px solid #d9dee7;
  background: #f8f9fb;
  color: #394354;
  border-radius: 18px;
  padding: 18px 16px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.suburb-pill.active {
  background: linear-gradient(135deg, #ff6f88, #ff5b76);
  border-color: transparent;
  color: white;
  box-shadow: 0 10px 20px rgba(255, 82, 115, 0.2);
}

.updated-row {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #778090;
  font-size: 15px;
  font-weight: 600;
}

.updated-dot {
  font-size: 16px;
}

.risk-summary-card {
  position: relative;
  min-height: 300px;
  border-radius: 30px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  margin-bottom: 52px;
  border: 1px solid #f3d8dc;
}

.risk-summary-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.risk-summary-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 243, 245, 0.92);
}

.risk-summary-content {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 26px;
  align-items: flex-start;
  padding: 44px 46px;
  max-width: 980px;
}

.risk-summary-icon {
  width: 96px;
  height: 96px;
  min-width: 96px;
  border-radius: 50%;
  background: #f8cdd4;
  display: grid;
  place-items: center;
  font-size: 42px;
}

.risk-summary-tag {
  margin: 6px 0 14px;
  color: #ef2f55;
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.risk-summary-content h2 {
  margin: 0 0 14px;
  font-size: 36px;
  font-weight: 500;
  line-height: 1.15;
}

.risk-summary-text {
  margin: 0;
  max-width: 760px;
  color: #475467;
  font-size: 18px;
  line-height: 1.7;
}

.sites-section {
  margin-bottom: 56px;
}

.site-list {
  display: grid;
  gap: 22px;
}

.site-card {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
  border-radius: 28px;
  padding: 34px 40px;
  box-shadow: var(--shadow-soft);
  border: 1px solid transparent;
}

.site-card.high {
  background: #fdf0f1;
  border-color: #f4d4d9;
}

.site-card.moderate {
  background: #f7f3e4;
  border-color: #f1da8b;
}

.site-card.low {
  background: #e4f5ee;
  border-color: #bde9d3;
}

.site-copy h3 {
  margin: 0 0 12px;
  font-size: 28px;
  font-weight: 500;
}

.site-type {
  margin: 0 0 18px;
  color: #5d6776;
  font-size: 18px;
}

.site-distance {
  margin: 0;
  color: #374253;
  font-size: 16px;
  font-weight: 700;
}

.site-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 122px;
  border-radius: 999px;
  padding: 14px 20px;
  font-size: 15px;
  font-weight: 800;
}

.site-badge.high {
  background: #f9dfe4;
  color: #e33a60;
  border: 1px solid #f1bac4;
}

.site-badge.moderate {
  background: #f7ecc8;
  color: #d07a13;
  border: 1px solid #efcf73;
}

.site-badge.low {
  background: #d9f4e7;
  color: #14805f;
  border: 1px solid #a8e2c8;
}

.dust-actions-panel {
  position: relative;
  min-height: 360px;
  border-radius: 30px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.dust-actions-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dust-actions-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8, 150, 123, 0.9),
    rgba(8, 150, 123, 0.78)
  );
}

.dust-actions-content {
  position: relative;
  z-index: 2;
  padding: 50px 56px;
  color: white;
  max-width: 820px;
}

.dust-actions-content h2 {
  margin: 0 0 26px;
  font-size: 34px;
  font-weight: 500;
}

.dust-actions-list {
  margin: 0 0 34px;
  padding-left: 22px;
}

.dust-actions-list li {
  margin-bottom: 20px;
  font-size: 18px;
  line-height: 1.6;
}

.dust-actions-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: white;
  color: #0f7f67;
  border-radius: 999px;
  padding: 18px 30px;
  font-size: 18px;
  font-weight: 700;
  text-decoration: none;
}

@media (max-width: 1100px) {
  .suburb-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 992px) {
  .hero-copy h1 {
    font-size: 54px;
  }

  .suburb-card {
    padding: 30px 26px;
  }

  .risk-summary-content {
    padding: 34px 28px;
  }

  .site-card {
    padding: 28px;
  }

  .dust-actions-content {
    padding: 36px 30px;
  }
}

@media (max-width: 768px) {
  .dust-hero {
    padding: 40px 0 56px;
  }

  .hero-brand {
    flex-wrap: wrap;
  }

  .hero-copy h1 {
    font-size: 42px;
    max-width: 100%;
  }

  .hero-copy p {
    font-size: 18px;
  }

  .suburb-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .risk-summary-content,
  .site-card {
    flex-direction: column;
  }

  .risk-summary-icon {
    width: 82px;
    height: 82px;
    min-width: 82px;
    font-size: 36px;
  }

  .risk-summary-content h2,
  .suburb-card h2,
  .sites-section h2 {
    font-size: 28px;
  }

  .site-copy h3 {
    font-size: 24px;
  }

  .dust-actions-content h2 {
    font-size: 28px;
  }

  .dust-actions-list li,
  .site-type,
  .suburb-card p {
    font-size: 16px;
  }

  .dust-actions-btn {
    font-size: 16px;
    padding: 16px 24px;
  }
}
</style>