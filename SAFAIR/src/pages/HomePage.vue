<template>
  <div class="home-page">
    <section class="hero-section">
      <div class="container hero-grid">
        <div class="hero-copy">
          <h1>They deserve to breathe easy</h1>
          <p>
            Stay ahead of asthma triggers in Melbourne. Help your child stay safe,
            active, and confident.
          </p>

          <router-link to="/insights" class="hero-btn">
            See what your child needs today
            <span>→</span>
          </router-link>
        </div>

        <div class="hero-image-wrap">
          <img
            src="../assets/images/hero-family.jpg"
            alt="Parent and child outdoors"
            class="hero-image"
          />
        </div>
      </div>
    </section>

    <section class="stats-section section">
      <div class="container">
        <h2>Asthma affects more families than you think</h2>

        <div class="stats-grid">
          <article
            v-for="stat in stats"
            :key="stat.title"
            class="stat-info-card"
          >
            <div class="stat-icon">{{ stat.icon }}</div>
            <h3>{{ stat.value }}</h3>
            <p class="stat-label">{{ stat.title }}</p>
            <p class="stat-description">{{ stat.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="happening-section section">
      <div class="happening-overlay"></div>

      <div class="container happening-inner">
        <h2>What is happening in Melbourne</h2>

        <div class="happening-grid">
          <article
            v-for="item in happeningItems"
            :key="item.title"
            class="happening-card"
          >
            <span class="happening-dot"></span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <section id="important-update" class="important-update section">
      <div class="container">
        <p class="update-kicker">IMPORTANT UPDATE</p>

        <div class="update-card">
          <img
            src="../assets/images/construction-summary-bg.jpg"
            alt="Construction"
            class="update-bg"
          />
          <div class="update-overlay"></div>

          <div class="update-content">
            <div class="update-icon-wrap">
              <div class="update-icon">≋</div>
            </div>

            <div class="update-copy">
              <p class="update-tag">TAKE ACTION</p>
              <h2>Construction dust may affect your area</h2>
              <p class="update-subtext">
                Wind is carrying dust toward your location today
              </p>

              <ul class="update-list">
                <li>Keep windows and doors closed</li>
                <li>Limit outdoor activity near construction sites</li>
                <li>Keep your child's inhaler accessible</li>
              </ul>

              <router-link to="/construction-dust" class="update-btn">
                View dust alerts
                <span>→</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="explore-section section">
      <div class="container">
        <h2>Choose how you want to stay prepared</h2>

        <div class="explore-grid">
          <article
            v-for="card in exploreCards"
            :key="card.title"
            class="explore-card"
          >
            <div class="explore-corner" :class="card.cornerClass"></div>

            <div class="explore-icon" :class="card.iconClass">
              {{ card.icon }}
            </div>

            <h3>{{ card.title }}</h3>
            <p>{{ card.description }}</p>

            <router-link :to="card.to" class="explore-link">
              Explore
              <span>→</span>
            </router-link>
          </article>
        </div>
      </div>
    </section>

    <section class="closing-section section">
      <div class="container closing-grid">
        <div class="closing-copy">
          <h2>Because every breath matters</h2>
          <p>
            We know how it feels to worry about triggers you cannot see. SAFAIR
            brings Melbourne's environmental data into one place and turns it into
            simple guidance you can trust.
          </p>
          <p>
            No medical jargon. No guesswork. Just practical guidance to help your
            child stay active, confident, and safe.
          </p>
        </div>

        <div class="closing-image-wrap">
          <img
            src="../assets/images/because-family.jpeg"
            alt="Family holding child"
            class="closing-image"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
const stats = [
  {
    icon: '◎',
    value: '386,000',
    title: 'CHILDREN LIVE WITH ASTHMA',
    description: 'One of the most common health conditions in Australia',
  },
  {
    icon: '⌁',
    value: '42%',
    title: 'MISS SCHOOL BECAUSE OF ASTHMA',
    description: 'It impacts learning, play, and daily life',
  },
  {
    icon: '△',
    value: '26,500',
    title: 'EMERGENCY VISITS EACH YEAR',
    description: 'Attacks can escalate quickly without warning',
  },
  {
    icon: '☰',
    value: 'Only 2 in 3',
    title: 'CHILDREN HAVE AN ACTION PLAN',
    description: 'Many families are not fully prepared',
  },
]

const happeningItems = [
  {
    title: 'Air quality changes throughout the day',
    description: 'Some times are safer for outdoor activity',
  },
  {
    title: 'Pollen levels can rise quickly',
    description: 'Even short exposure can trigger symptoms',
  },
  {
    title: 'Construction dust can travel with wind',
    description: 'Risk depends on direction and distance',
  },
]

const exploreCards = [
  {
    title: 'View Air Quality Insights',
    description: 'See what is in the air today',
    icon: '◌',
    to: '/insights',
    iconClass: 'green',
    cornerClass: 'mint',
  },
  {
    title: 'Track Construction Dust',
    description: 'Check nearby dust risks',
    icon: '≋',
    to: '/construction-dust',
    iconClass: 'coral',
    cornerClass: 'pink',
  },
  {
    title: 'See Safe Times for Outdoor Activity',
    description: 'Find better times for play and exercise',
    icon: '⌁',
    to: '/insights',
    iconClass: 'blue',
    cornerClass: 'blue',
  },
  {
    title: 'Get Personalised Recommendations',
    description: "Simple steps based on today's conditions",
    icon: '☑',
    to: '/recommendations',
    iconClass: 'green',
    cornerClass: 'mint',
  },
]
</script>

<style scoped>
.home-page {
  background: var(--bg-page);
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #08a183, #0f8b8f);
  padding: 72px 0 82px;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 52px;
  align-items: center;
}

.hero-copy h1 {
  margin: 0 0 24px;
  max-width: 520px;
  font-size: 64px;
  line-height: 1.05;
  font-weight: 400;
  color: white;
}

.hero-copy p {
  margin: 0 0 30px;
  max-width: 620px;
  font-size: 18px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.95);
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: white;
  color: #0d7f71;
  text-decoration: none;
  border-radius: 999px;
  padding: 18px 34px;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 14px 26px rgba(0, 0, 0, 0.08);
}

.hero-image-wrap {
  display: flex;
  justify-content: flex-end;
}

.hero-image {
  width: 100%;
  max-width: 560px;
  height: 420px;
  object-fit: cover;
  border-radius: 28px;
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.12);
}

.stats-section h2,
.happening-inner h2,
.explore-section h2,
.closing-copy h2 {
  margin: 0 0 30px;
  font-size: 52px;
  line-height: 1.08;
  font-weight: 400;
  color: #181f2f;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 24px;
}

.stat-info-card {
  background: white;
  border-radius: 24px;
  padding: 28px 28px 26px;
  box-shadow: var(--shadow-soft);
}

.stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  background: linear-gradient(135deg, #13b7a2, #0aa174);
  color: white;
  display: grid;
  place-items: center;
  font-size: 20px;
  margin-bottom: 22px;
  box-shadow: 0 10px 18px rgba(19, 183, 162, 0.16);
}

.stat-info-card h3 {
  margin: 0 0 10px;
  font-size: 28px;
  line-height: 1.15;
  font-weight: 500;
  color: #1d2431;
}

.stat-label {
  margin: 0 0 16px;
  font-size: 13px;
  line-height: 1.5;
  letter-spacing: 0.04em;
  color: #4f5a6b;
  font-weight: 800;
}

.stat-description {
  margin: 0;
  color: #5b6778;
  font-size: 15px;
  line-height: 1.7;
}

.happening-section {
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(rgba(236, 244, 250, 0.85), rgba(236, 244, 250, 0.87)),
    url('@/assets/images/melbourne-skyline-bg.jpg') center/cover no-repeat;
}

.happening-overlay {
  position: absolute;
  inset: 0;
  background: rgba(240, 247, 249, 0.35);
}

.happening-inner {
  position: relative;
  z-index: 2;
}

.happening-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px;
}

.happening-card {
  background: white;
  border-radius: 24px;
  padding: 30px 34px 28px;
  box-shadow: var(--shadow-soft);
}

.happening-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #13b7a2;
  display: inline-block;
  margin-bottom: 22px;
}

.happening-card h3 {
  margin: 0 0 16px;
  font-size: 22px;
  line-height: 1.4;
  font-weight: 500;
  color: #1c2430;
}

.happening-card p {
  margin: 0;
  color: #586476;
  font-size: 15px;
  line-height: 1.7;
}

.important-update {
  margin-top: 56px;
  padding-top: 10px;
}

.update-kicker {
  margin: 0 0 16px;
  color: #ff2f64;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.update-card {
  position: relative;
  min-height: 420px;
  border-radius: 28px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  border: 1px solid #f0d7db;
}

.update-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.update-overlay {
  position: absolute;
  inset: 0;
  background: rgba(251, 239, 241, 0.9);
}

.update-content {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 26px;
  max-width: 720px;
  padding: 46px 48px;
}

.update-icon-wrap {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.update-icon {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f0627e, #d87a46);
  color: white;
  display: grid;
  place-items: center;
  font-size: 34px;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08);
}

.update-tag {
  margin: 8px 0 12px;
  color: #ef2f55;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.update-copy h2 {
  margin: 0 0 16px;
  font-size: 28px;
  line-height: 1.15;
  font-weight: 500;
  color: #1f2430;
}

.update-subtext {
  margin: 0 0 22px;
  color: #445062;
  font-size: 16px;
  line-height: 1.7;
}

.update-list {
  margin: 0 0 28px;
  padding-left: 20px;
  color: #374253;
}

.update-list li {
  margin-bottom: 16px;
  font-size: 16px;
  line-height: 1.6;
}

.update-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  background: linear-gradient(135deg, #f0627e, #d87a46);
  color: white;
  border-radius: 999px;
  padding: 16px 30px;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 12px 24px rgba(216, 122, 70, 0.2);
}

.explore-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

.explore-card {
  position: relative;
  background: white;
  border-radius: 24px;
  padding: 36px 36px 34px;
  box-shadow: var(--shadow-soft);
  overflow: hidden;
  min-height: 250px;
}

.explore-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 82px;
  height: 82px;
  border-bottom-left-radius: 100%;
}

.explore-corner.mint {
  background: #e0f2ec;
}

.explore-corner.pink {
  background: #f6dde3;
}

.explore-corner.blue {
  background: #dce8f8;
}

.explore-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: white;
  font-size: 22px;
  margin-bottom: 24px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
}

.explore-icon.green {
  background: linear-gradient(135deg, #13b7a2, #0aa174);
}

.explore-icon.coral {
  background: linear-gradient(135deg, #f0627e, #d87a46);
}

.explore-icon.blue {
  background: linear-gradient(135deg, #2f80ff, #0f91d8);
}

.explore-card h3 {
  margin: 0 0 16px;
  font-size: 22px;
  line-height: 1.4;
  font-weight: 500;
  color: #1f2430;
}

.explore-card p {
  margin: 0 0 22px;
  color: #5b6778;
  font-size: 15px;
  line-height: 1.7;
}

.explore-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #009688;
  font-size: 15px;
  font-weight: 700;
}

.closing-section {
  background: linear-gradient(180deg, #edf3f9 0%, #f2f7f5 100%);
}

.closing-grid {
  display: grid;
  grid-template-columns: 1fr 0.95fr;
  gap: 52px;
  align-items: center;
}

.closing-copy h2 {
  max-width: 460px;
}

.closing-copy p {
  margin: 0 0 22px;
  max-width: 580px;
  color: #495567;
  font-size: 18px;
  line-height: 1.75;
}

.closing-image-wrap {
  display: flex;
  justify-content: flex-end;
}

.closing-image {
  width: 100%;
  max-width: 560px;
  height: 500px;
  object-fit: cover;
  border-radius: 28px;
  box-shadow: var(--shadow-soft);
}

@media (max-width: 1200px) {
  .hero-grid,
  .closing-grid {
    grid-template-columns: 1fr;
  }

  .hero-image-wrap,
  .closing-image-wrap {
    justify-content: flex-start;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 992px) {
  .hero-copy h1,
  .stats-section h2,
  .happening-inner h2,
  .explore-section h2,
  .closing-copy h2 {
    font-size: 42px;
  }

  .happening-grid,
  .explore-grid {
    grid-template-columns: 1fr;
  }

  .update-content {
    grid-template-columns: 1fr;
    padding: 34px 26px;
  }

  .update-icon-wrap {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 56px 0 68px;
  }

  .hero-copy h1,
  .stats-section h2,
  .happening-inner h2,
  .explore-section h2,
  .closing-copy h2 {
    font-size: 34px;
    max-width: 100%;
  }

  .hero-copy p,
  .closing-copy p {
    font-size: 16px;
  }

  .hero-btn,
  .update-btn {
    width: 100%;
    justify-content: center;
  }

  .hero-image,
  .closing-image {
    height: 340px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-info-card,
  .happening-card,
  .explore-card {
    padding: 24px 20px;
  }

  .stat-info-card h3 {
    font-size: 24px;
  }

  .update-copy h2 {
    font-size: 24px;
  }

  .update-subtext,
  .update-list li,
  .happening-card p,
  .explore-card p {
    font-size: 15px;
  }
}
</style>