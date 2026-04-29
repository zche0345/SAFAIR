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
import { ref, onMounted, onBeforeUnmount } from 'vue'

const scrollProgress = ref(0)

const handleScroll = () => {
  const scrollTop = window.scrollY
  const docHeight =
    document.documentElement.scrollHeight - window.innerHeight

  scrollProgress.value = (scrollTop / docHeight) * 100
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

  .learn-categories,
  .resources-grid,
  .topics-grid {
    grid-template-columns: 1fr;
  }

  .learn-title {
    font-size: 3.5rem;
  }
}
</style>