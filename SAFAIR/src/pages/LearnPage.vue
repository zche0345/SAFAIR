<template>
  <div class="learn-page">
    <!-- Progress Bar -->
    <div class="scroll-progress">
      <div class="scroll-progress__bar" :style="{ width: scrollProgress + '%' }"></div>
    </div>

    <!-- HERO -->
    <section class="learn-hero">
      <div class="learn-hero__content">
        <router-link to="/" class="back-link">
          ← Back to Home
        </router-link>

        <h1 class="learn-title">
          Learn About <span>Asthma &<br />Air Quality</span>
        </h1>

        <p class="learn-subtitle">
          Evidence-based guides to help you understand triggers,
          manage symptoms, and protect your family
        </p>
      </div>

      <div class="learn-hero__image-wrapper floating-image">
        <img
          src="@/assets/images/learn-hero.jpg"
          alt="Learning resources"
          class="learn-hero__image"
        />
      </div>
    </section>

    <!-- ASTHMA STATISTICS -->
    <section class="asthma-stats-section">
      <div class="stats-header reveal-card">
        <span class="stats-eyebrow">Asthma in Australia</span>
        <h2>Why asthma awareness matters</h2>
        <p>
          These simple statistics show why asthma education, air quality awareness,
          and trigger management are important for families.
        </p>
      </div>

      <div class="stats-split-layout reveal-card">
        <div class="stats-sidebar" aria-label="Asthma statistic options">
          <button
            v-for="(stat, index) in asthmaStats"
            :key="stat.label"
            class="stat-link"
            :class="{ active: selectedStat === index }"
            type="button"
            @click="selectStat(index)"
          >
            <span class="stat-link-icon" :style="{ background: stat.bg }">
              {{ stat.icon }}
            </span>

            <span class="stat-link-text">
              <strong>{{ stat.shortLabel }}</strong>
              <small>{{ stat.value }}</small>
            </span>
          </button>
        </div>

        <div class="stat-display-card">
          <div class="stat-display-top">
            <div
              class="stat-icon stat-display-icon"
              :style="{ background: activeStat.bg }"
            >
              {{ activeStat.icon }}
            </div>

            <span class="stat-display-tag">Selected statistic</span>
          </div>

          <div class="stat-display-main">
            <p class="stat-display-label">{{ activeStat.label }}</p>
            <h3>{{ activeStat.value }}</h3>
            <p class="stat-display-description">
              {{ activeStat.description }}
            </p>
          </div>

          <div class="stat-info-grid">
            <div class="stat-info-box">
              <strong>What this means</strong>
              <p>{{ activeStat.detail }}</p>
            </div>

            <div class="stat-info-box">
              <strong>Why BRTHEZ cares</strong>
              <p>{{ activeStat.brthezLink }}</p>
            </div>
          </div>
        </div>
      </div>

      <p class="stats-source reveal-card">
        Source: Australian Institute of Health and Welfare, Australian Bureau of Statistics,
        Asthma Australia, and National Asthma Council Australia.
      </p>
    </section>

    <!-- DETAILED ASTHMA RATES -->
    <section class="asthma-rates-section">
      <div class="rates-header reveal-card">
        <span class="stats-eyebrow">Detailed asthma rates</span>
        <h2>How asthma rates differ across groups</h2>
        <p>
          These visual components use published Australian asthma data to show
          how rates vary by age, sex, location type, and disadvantage level.
        </p>
      </div>

      <div class="rates-grid">
        <div class="rate-chart-card reveal-card wide-chart-card">
          <div class="chart-card-header">
            <div>
              <h3>Asthma prevalence by age and sex, 2022</h3>
              <p>
                The chart compares male and female asthma prevalence across age groups.
                Values are percentages of people in each group.
              </p>
            </div>

            <div class="chart-legend" aria-label="Chart legend">
              <span><i class="legend-box male"></i> Males</span>
              <span><i class="legend-box female"></i> Females</span>
            </div>
          </div>

          <div class="grouped-bar-chart" role="img" aria-label="Bar chart showing asthma prevalence by age and sex in 2022">
            <div class="chart-y-axis">
              <span>16%</span>
              <span>12%</span>
              <span>8%</span>
              <span>4%</span>
              <span>0%</span>
            </div>

            <div class="chart-plot-area">
              <div class="chart-grid-lines" aria-hidden="true">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
              </div>

              <div
                v-for="row in asthmaByAgeSex"
                :key="row.ageGroup"
                class="age-bar-group"
              >
                <div class="bar-pair">
                  <div
                    class="bar male-bar"
                    :style="{ height: getBarHeight(row.male) }"
                    :title="`Males ${row.ageGroup}: ${row.male}%`"
                  >
                    <span>{{ row.male }}%</span>
                  </div>

                  <div
                    class="bar female-bar"
                    :style="{ height: getBarHeight(row.female) }"
                    :title="`Females ${row.ageGroup}: ${row.female}%`"
                  >
                    <span>{{ row.female }}%</span>
                  </div>
                </div>

                <p>{{ row.ageGroup }}</p>
              </div>
            </div>
          </div>

          <p class="chart-note">
            Main reading: asthma is higher for boys than girls in ages 0–14, while
            female rates are higher than male rates across most older age groups.
          </p>
        </div>

        <div class="rate-chart-card reveal-card">
          <div class="chart-card-header compact">
            <div>
              <h3>Rates by location type</h3>
              <p>
                AIHW reports little difference by remoteness, but regional areas
                are slightly higher than major cities.
              </p>
            </div>
          </div>

          <div class="simple-rate-list">
            <div
              v-for="item in remotenessRates"
              :key="item.label"
              class="simple-rate-row"
            >
              <div class="simple-rate-top">
                <span>{{ item.label }}</span>
                <strong>{{ item.rate }}%</strong>
              </div>

              <div class="simple-rate-track">
                <div
                  class="simple-rate-fill"
                  :style="{ width: getRateWidth(item.rate) }"
                ></div>
              </div>
            </div>
          </div>

          <p class="chart-note">
            This helps users understand that asthma risk is not limited to one
            location type only.
          </p>
        </div>

        <div class="rate-chart-card reveal-card">
          <div class="chart-card-header compact">
            <div>
              <h3>Rates by disadvantage level</h3>
              <p>
                ABS 2022 data shows higher asthma prevalence in the most
                disadvantaged areas compared with the least disadvantaged areas.
              </p>
            </div>
          </div>

          <div class="comparison-cards">
            <div
              v-for="item in disadvantageRates"
              :key="item.label"
              class="comparison-card"
            >
              <span>{{ item.label }}</span>
              <strong>{{ item.rate }}%</strong>
              <div class="comparison-track">
                <div
                  class="comparison-fill"
                  :style="{ width: getRateWidth(item.rate) }"
                ></div>
              </div>
            </div>
          </div>

          <p class="chart-note">
            This is useful for BRTHEZ because environmental health support should
            stay simple and accessible for all families.
          </p>
        </div>
      </div>

      <div class="data-limitation-card reveal-card">
        <strong>Data note</strong>
        <p>
          These charts use national Australian estimates from ABS and AIHW. The values
          explain broad asthma patterns, not individual medical risk. Local asthma
          experience can vary based on suburb, triggers, housing, weather, medication,
          and personal health history.
        </p>
      </div>
    </section>

    <!-- FEATURED TOPICS -->
    <section class="learn-categories">
      <div
        v-for="category in categories"
        :key="category.title"
        class="learn-category-card reveal-card"
      >
        <div
          class="learn-category-icon"
          :style="{ background: category.bg }"
        >
          {{ category.icon }}
        </div>

        <h3>{{ category.title }}</h3>

        <p>{{ category.description }}</p>

        <button
          class="learn-category-btn"
          :style="{ color: category.color }"
        >
          Explore guides →
        </button>
      </div>
    </section>

    <!-- POPULAR TOPICS -->
    <section class="popular-topics">
      <h2>Popular topics</h2>

      <div class="topics-grid">
        <div
          v-for="topic in topics"
          :key="topic.title"
          class="topic-card reveal-card"
        >
          <div>
            <h3>{{ topic.title }}</h3>
            <span>{{ topic.tag }}</span>
          </div>

          <div class="topic-arrow">→</div>
        </div>
      </div>
    </section>

    <!-- TRUSTED RESOURCES -->
    <section class="trusted-resources">
      <h2>Trusted resources</h2>

      <div class="resources-grid">
        <div
          v-for="resource in resources"
          :key="resource.name"
          class="resource-card reveal-card"
        >
          <h3>{{ resource.name }}</h3>
          <p>{{ resource.description }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const scrollProgress = ref(0)
const selectedStat = ref(0)

const handleScroll = () => {
  const scrollTop = window.scrollY
  const docHeight =
    document.documentElement.scrollHeight - window.innerHeight

  scrollProgress.value = (scrollTop / docHeight) * 100
}

const activeStat = computed(() => asthmaStats[selectedStat.value])

const selectStat = (index) => {
  selectedStat.value = index
}

const getBarHeight = (value) => {
  const maxValue = 16
  return `${Math.max((value / maxValue) * 100, 4)}%`
}

const getRateWidth = (value) => {
  const maxValue = 16
  return `${Math.max((value / maxValue) * 100, 6)}%`
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed')
        }
      })
    },
    { threshold: 0.15 }
  )

  document.querySelectorAll('.reveal-card').forEach((el) => {
    observer.observe(el)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})

const asthmaStats = [
  {
    icon: '🇦🇺',
    value: '2.8M',
    label: 'Australians with asthma',
    shortLabel: 'Australians',
    description:
      'Around one in nine Australians are estimated to be living with asthma.',
    detail:
      'Asthma is not a rare condition. It affects everyday routines, school, work, exercise, and family planning.',
    brthezLink:
      'BRTHEZ helps users connect asthma awareness with daily environmental risks like pollen, dust, and air quality.',
    bg: '#EDF7F5'
  },
  {
    icon: '📊',
    value: '10.8%',
    label: 'National asthma rate',
    shortLabel: 'National rate',
    description:
      'Just under 11% of Australians had asthma in 2022.',
    detail:
      'This means asthma affects a large share of the population, not only a small high-risk group.',
    brthezLink:
      'This supports the need for simple public-facing tools that make risk information easier to understand.',
    bg: '#EEF3FF'
  },
  {
    icon: '🧒',
    value: '386K',
    label: 'Children under 15',
    shortLabel: 'Children',
    description:
      'Around 386,000 Australian children under 15 live with asthma.',
    detail:
      'Children are a key risk group because symptoms can affect school, sport, sleep, and family routines.',
    brthezLink:
      'This connects strongly with BRTHEZ’s guardian and teenager user stories.',
    bg: '#FFF2EC'
  },
  {
    icon: '📝',
    value: '32.1%',
    label: 'Have an action plan',
    shortLabel: 'Action plans',
    description:
      'Only around one in three people with asthma had a written asthma action plan in 2022.',
    detail:
      'A written action plan helps people know what to do when symptoms increase or when risk conditions change.',
    brthezLink:
      'BRTHEZ can support safer decision-making by giving users easy reminders and awareness content.',
    bg: '#F3EEFF'
  },
  {
    icon: '💊',
    value: '33.9%',
    label: 'Use daily medication',
    shortLabel: 'Daily medicine',
    description:
      'About one in three people with asthma used asthma medication every day in 2022.',
    detail:
      'Daily medication use shows that asthma management is ongoing, not just something people think about during attacks.',
    brthezLink:
      "This supports BRTHEZ's focus on everyday recommendations, not only emergency warnings.",
    bg: '#FFF7E6'
  },
  {
    icon: '🏥',
    value: '43%',
    label: 'Child hospitalisations',
    shortLabel: 'Hospital care',
    description:
      'Almost half of asthma hospitalisations in 2023–2024 were for children aged 14 or under.',
    detail:
      'Hospitalisation data shows that asthma can become serious, especially for younger users and families.',
    brthezLink:
      'This makes the Learn Page useful because it explains prevention, triggers, and safer daily choices.',
    bg: '#EDF8F0'
  }
]

const asthmaByAgeSex = [
  { ageGroup: '0–14', male: 10.1, female: 6.2 },
  { ageGroup: '15–24', male: 8.4, female: 12.3 },
  { ageGroup: '25–34', male: 9.2, female: 10.5 },
  { ageGroup: '35–44', male: 9.8, female: 15.8 },
  { ageGroup: '45–54', male: 9.9, female: 14.3 },
  { ageGroup: '55–64', male: 8.6, female: 15.3 },
  { ageGroup: '65–74', male: 9.3, female: 13.7 },
  { ageGroup: '75+', male: 10.7, female: 12.7 }
]

const remotenessRates = [
  { label: 'Major cities', rate: 10 },
  { label: 'Inner regional', rate: 12 },
  { label: 'Outer regional / remote', rate: 12 }
]

const disadvantageRates = [
  { label: 'Most disadvantaged areas', rate: 13 },
  { label: 'Least disadvantaged areas', rate: 10 }
]

const categories = [
  {
    icon: '💨',
    title: 'Understanding Air Quality',
    description:
      'Learn what PM2.5, NO2, and ozone mean for your family',
    color: '#0F8C7C',
    bg: '#EDF7F5'
  },
  {
    icon: '🏥',
    title: 'Managing Asthma',
    description:
      'Action plans, emergency response, and daily care tips',
    color: '#F26B3A',
    bg: '#FFF2EC'
  },
  {
    icon: '🏡',
    title: 'Indoor Air Safety',
    description:
      'Create a safer home environment for sensitive airways',
    color: '#2C8A52',
    bg: '#EDF8F0'
  }
]

const topics = [
  {
    title: 'What triggers asthma attacks in children?',
    tag: 'BASICS'
  },
  {
    title: 'How to read your asthma action plan',
    tag: 'MANAGEMENT'
  },
  {
    title: 'Construction dust: What parents should know',
    tag: 'OUTDOOR AIR'
  },
  {
    title: 'Safe cleaning products for asthma families',
    tag: 'INDOOR AIR'
  },
  {
    title: 'When to use a spacer vs nebulizer',
    tag: 'MEDICATION'
  },
  {
    title: 'Exercise and asthma: Staying active safely',
    tag: 'LIFESTYLE'
  }
]

const resources = [
  {
    name: 'Asthma Australia',
    description: 'National support organization'
  },
  {
    name: 'EPA Victoria',
    description: 'Air quality data & reports'
  },
  {
    name: "Royal Children's Hospital",
    description: 'Clinical guidelines'
  },
  {
    name: 'Allergy & Anaphylaxis',
    description: 'Trigger management'
  }
]
</script>

<style scoped>
.learn-page {
  background: #f8f7f4;
  min-height: 100vh;
}

/* PROGRESS BAR */

.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: transparent;
  z-index: 9999;
}

.scroll-progress__bar {
  height: 100%;
  background: linear-gradient(90deg, #2d4fa3, #34c7b0);
  transition: width 0.1s linear;
}

/* HERO */

.learn-hero {
  width: 100%;
  padding: 70px 80px 90px;
  background: linear-gradient(135deg, #24488f 0%, #37c6b3 100%);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
  align-items: center;
}

.back-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 0.95rem;
  margin-bottom: 28px;
  display: inline-block;
}

.learn-title {
  font-size: 4.3rem;
  line-height: 0.95;
  color: white;
  margin-bottom: 22px;
  font-family: "Cormorant Garamond", serif;
  font-weight: 500;
}

.learn-title span {
  font-style: italic;
}

.learn-subtitle {
  color: rgba(255, 255, 255, 0.92);
  font-size: 1.12rem;
  line-height: 1.6;
  max-width: 620px;
}

.learn-hero__image-wrapper {
  display: flex;
  justify-content: center;
}

.learn-hero__image {
  width: 100%;
  max-width: 680px;
  height: 340px;
  object-fit: cover;
  border-radius: 28px;
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.22);
}

/* FLOAT */

.floating-image {
  animation: floating 6s ease-in-out infinite;
}

@keyframes floating {
  0% {
    transform: translateY(0px);
  }

  50% {
    transform: translateY(-14px);
  }

  100% {
    transform: translateY(0px);
  }
}

/* ASTHMA STATISTICS */

.asthma-stats-section,
.asthma-rates-section {
  width: calc(100% - 160px);
  margin: 70px auto 80px;
}

.stats-header,
.rates-header {
  max-width: 780px;
  margin-bottom: 28px;
}

.stats-eyebrow {
  display: inline-block;
  color: #0f8c7c;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.stats-header h2,
.rates-header h2 {
  font-size: 3rem;
  font-family: "Cormorant Garamond", serif;
  color: #1f2937;
  margin-bottom: 14px;
}

.stats-header p,
.rates-header p {
  color: #5e6878;
  font-size: 1rem;
  line-height: 1.7;
}

.stats-split-layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 24px;
  align-items: stretch;
}

.stats-sidebar {
  background: white;
  border: 1px solid #ececec;
  border-radius: 26px;
  padding: 16px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.05);
  display: grid;
  gap: 10px;
}

.stat-link {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 13px;
  text-align: left;
  border: 1px solid transparent;
  background: transparent;
  border-radius: 18px;
  padding: 13px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.25s ease;
}

.stat-link:hover,
.stat-link.active {
  background: #f7fffd;
  border-color: rgba(52, 199, 176, 0.55);
  transform: translateX(4px);
}

.stat-link-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.stat-link-text {
  display: grid;
  gap: 4px;
}

.stat-link-text strong {
  color: #1d2a39;
  font-size: 0.95rem;
}

.stat-link-text small {
  color: #24488f;
  font-size: 0.9rem;
  font-weight: 800;
}

.stat-display-card {
  background: white;
  border: 1px solid #ececec;
  border-radius: 30px;
  padding: 34px;
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.07);
  min-height: 430px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.stat-display-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 26px;
}

.stat-icon {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.stat-display-tag {
  color: #0f8c7c;
  background: #edf7f5;
  border-radius: 999px;
  padding: 8px 13px;
  font-size: 0.78rem;
  font-weight: 800;
}

.stat-display-main {
  margin-bottom: 28px;
}

.stat-display-label {
  color: #1d2a39;
  font-size: 1.1rem;
  font-weight: 800;
  margin-bottom: 10px;
}

.stat-display-main h3 {
  font-size: 5rem;
  line-height: 0.95;
  color: #24488f;
  margin-bottom: 18px;
  letter-spacing: -2px;
}

.stat-display-description {
  max-width: 760px;
  color: #5e6878;
  font-size: 1.05rem;
  line-height: 1.7;
}

.stat-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-info-box {
  background: #f8faf9;
  border: 1px solid #e6f3f0;
  border-radius: 20px;
  padding: 20px;
}

.stat-info-box strong {
  display: block;
  color: #1d2a39;
  font-size: 0.92rem;
  margin-bottom: 8px;
}

.stat-info-box p {
  color: #6b7280;
  font-size: 0.92rem;
  line-height: 1.65;
}

.stats-source {
  margin-top: 16px;
  color: #7b8598;
  font-size: 0.85rem;
  line-height: 1.5;
}

/* DETAILED RATES */

.asthma-rates-section {
  margin-top: -28px;
}

.rates-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}

.rate-chart-card {
  background: white;
  border: 1px solid #ececec;
  border-radius: 26px;
  padding: 26px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.05);
}

.wide-chart-card {
  grid-column: 1 / -1;
}

.chart-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.chart-card-header.compact {
  display: block;
}

.chart-card-header h3 {
  font-size: 1.55rem;
  color: #1d2a39;
  margin-bottom: 8px;
  font-family: "Cormorant Garamond", serif;
}

.chart-card-header p {
  color: #5e6878;
  font-size: 0.95rem;
  line-height: 1.65;
  max-width: 760px;
}

.chart-legend {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.chart-legend span {
  display: flex;
  align-items: center;
  gap: 7px;
  color: #4b5563;
  font-size: 0.86rem;
  font-weight: 700;
}

.legend-box {
  width: 13px;
  height: 13px;
  border-radius: 4px;
  display: inline-block;
}

.legend-box.male {
  background: #24488f;
}

.legend-box.female {
  background: #34c7b0;
}

.grouped-bar-chart {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 14px;
  min-height: 330px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #7b8598;
  font-size: 0.78rem;
  padding-bottom: 32px;
  text-align: right;
}

.chart-plot-area {
  position: relative;
  display: grid;
  grid-template-columns: repeat(8, minmax(70px, 1fr));
  gap: 14px;
  align-items: end;
  border-left: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 10px 0;
  overflow-x: auto;
}

.chart-grid-lines {
  position: absolute;
  inset: 0 0 32px 0;
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  pointer-events: none;
}

.chart-grid-lines span {
  border-top: 1px dashed #eef2f2;
}

.age-bar-group {
  position: relative;
  z-index: 1;
  height: 100%;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 9px;
}

.bar-pair {
  height: 260px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 7px;
}

.bar {
  width: 28px;
  border-radius: 12px 12px 5px 5px;
  position: relative;
  min-height: 22px;
  transition: height 0.35s ease;
}

.bar span {
  position: absolute;
  left: 50%;
  top: -24px;
  transform: translateX(-50%);
  color: #1d2a39;
  font-size: 0.72rem;
  font-weight: 800;
  white-space: nowrap;
}

.male-bar {
  background: linear-gradient(180deg, #335cb8, #24488f);
}

.female-bar {
  background: linear-gradient(180deg, #58dbc9, #34c7b0);
}

.age-bar-group p {
  color: #5e6878;
  font-size: 0.78rem;
  font-weight: 700;
  text-align: center;
  min-height: 26px;
}

.simple-rate-list {
  display: grid;
  gap: 18px;
  margin-top: 20px;
}

.simple-rate-row {
  display: grid;
  gap: 9px;
}

.simple-rate-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.simple-rate-top span,
.comparison-card span {
  color: #1d2a39;
  font-size: 0.95rem;
  font-weight: 800;
}

.simple-rate-top strong,
.comparison-card strong {
  color: #24488f;
  font-size: 1.25rem;
}

.simple-rate-track,
.comparison-track {
  width: 100%;
  height: 12px;
  background: #eef3f2;
  border-radius: 999px;
  overflow: hidden;
}

.simple-rate-fill,
.comparison-fill {
  height: 100%;
  background: linear-gradient(90deg, #24488f, #34c7b0);
  border-radius: 999px;
}

.comparison-cards {
  display: grid;
  gap: 14px;
  margin-top: 20px;
}

.comparison-card {
  background: #f8faf9;
  border: 1px solid #e6f3f0;
  border-radius: 18px;
  padding: 18px;
  display: grid;
  gap: 10px;
}

.chart-note {
  margin-top: 18px;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.65;
}

.data-limitation-card {
  margin-top: 20px;
  background: #fffaf0;
  border: 1px solid #f3dfb8;
  border-radius: 20px;
  padding: 20px;
}

.data-limitation-card strong {
  display: block;
  color: #8a5a00;
  margin-bottom: 8px;
}

.data-limitation-card p {
  color: #6b5d45;
  font-size: 0.92rem;
  line-height: 1.65;
}

/* CATEGORY CARDS */

.learn-categories {
  width: calc(100% - 160px);
  margin: -45px auto 70px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

.learn-category-card {
  background: white;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  transition: all 0.35s ease;
}

.learn-category-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.12);
}

.learn-category-icon {
  width: 62px;
  height: 62px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.7rem;
  margin-bottom: 22px;
}

.learn-category-card h3 {
  font-size: 1.7rem;
  margin-bottom: 14px;
  color: #1d2a39;
  font-family: "Cormorant Garamond", serif;
}

.learn-category-card p {
  font-size: 0.98rem;
  line-height: 1.7;
  color: #5e6878;
  margin-bottom: 22px;
}

.learn-category-btn {
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
}

/* POPULAR TOPICS */

.popular-topics {
  width: calc(100% - 160px);
  margin: 0 auto 80px;
}

.popular-topics h2,
.trusted-resources h2 {
  font-size: 3.1rem;
  font-family: "Cormorant Garamond", serif;
  color: #1f2937;
  margin-bottom: 28px;
}

.topics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.topic-card {
  background: white;
  border-radius: 20px;
  padding: 26px;
  border: 1px solid #ececec;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.topic-card:hover {
  transform: translateY(-6px);
  border-color: #33c5b0;
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.08);
}

.topic-card h3 {
  font-size: 1.28rem;
  color: #222;
  margin-bottom: 12px;
}

.topic-card span {
  color: #7d8aa0;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 1px;
}

.topic-arrow {
  font-size: 1.6rem;
  color: #28b7a0;
}

/* RESOURCES */

.trusted-resources {
  width: calc(100% - 160px);
  margin: 0 auto 90px;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.resource-card {
  background: white;
  border-radius: 18px;
  border: 1px solid #ececec;
  padding: 24px;
  transition: all 0.3s ease;
}

.resource-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.08);
}

.resource-card h3 {
  font-size: 1.2rem;
  margin-bottom: 10px;
  color: #1d2a39;
}

.resource-card p {
  color: #7b8598;
  font-size: 0.92rem;
  line-height: 1.6;
}

/* REVEAL */

.reveal-card {
  opacity: 0;
  transform: translateY(50px);
  transition: all 0.7s ease;
}

.reveal-card.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* RESPONSIVE */

@media (max-width: 1200px) {
  .learn-hero,
  .asthma-stats-section,
  .asthma-rates-section,
  .learn-categories,
  .popular-topics,
  .trusted-resources {
    width: calc(100% - 60px);
    padding-left: 0;
    padding-right: 0;
  }

  .learn-hero {
    grid-template-columns: 1fr;
  }

  .stats-split-layout {
    grid-template-columns: 280px minmax(0, 1fr);
  }

  .stat-display-main h3 {
    font-size: 4rem;
  }

  .learn-categories,
  .resources-grid,
  .topics-grid,
  .rates-grid {
    grid-template-columns: 1fr;
  }

  .learn-title {
    font-size: 3.5rem;
  }

  .stats-header h2,
  .rates-header h2 {
    font-size: 2.4rem;
  }
}

@media (max-width: 700px) {
  .learn-hero {
    padding-top: 54px;
    padding-bottom: 70px;
  }

  .learn-title {
    font-size: 2.8rem;
  }

  .learn-hero__image {
    height: 250px;
  }

  .stats-split-layout {
    grid-template-columns: 1fr;
  }

  .stats-sidebar {
    display: flex;
    overflow-x: auto;
    gap: 10px;
    padding: 12px;
  }

  .stat-link {
    min-width: 170px;
  }

  .stat-link:hover,
  .stat-link.active {
    transform: translateY(-2px);
  }

  .stat-display-card {
    padding: 24px;
    min-height: auto;
  }

  .stat-display-main h3 {
    font-size: 3.2rem;
  }

  .stat-info-grid,
  .rates-grid {
    grid-template-columns: 1fr;
  }

  .chart-card-header {
    display: block;
  }

  .chart-legend {
    margin-top: 14px;
  }

  .grouped-bar-chart {
    grid-template-columns: 40px 1fr;
  }

  .chart-plot-area {
    grid-template-columns: repeat(8, 78px);
  }

  .bar {
    width: 24px;
  }
}
</style>
