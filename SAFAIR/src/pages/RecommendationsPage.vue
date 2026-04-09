<template>
  <div class="recommendations-page">
    <section class="recommendations-hero">
      <div class="container">
        <div class="brand-row">
          <div class="brand-left">
            <div class="brand-icon">✦</div>
            <span class="brand-name">SAFAIR</span>
            <router-link to="/insights" class="back-link">‹ Back to Insights</router-link>
          </div>
        </div>

        <div class="hero-copy">
          <h1>{{ page.heroTitle }}</h1>
          <p>{{ page.heroSubtitle }}</p>
        </div>
      </div>
    </section>

    <section class="section recommendations-content">
      <div class="container">
        <div class="support-banner">
          <img
            src="../assets/images/recommendations-hero-bg.jpg"
            alt="Children together"
            class="support-bg"
          />
          <div class="support-overlay"></div>

          <div class="support-content">
            <div class="support-icon">🛡</div>
            <div>
              <h2>{{ page.supportCard.title }}</h2>
              <p>{{ page.supportCard.text }}</p>
            </div>
          </div>
        </div>

        <div
          v-for="section in page.sections"
          :key="section.id"
          class="recommendation-group"
        >
          <div class="group-heading">
            <div class="group-icon">{{ section.icon }}</div>
            <div>
              <h2>
                {{ section.title }}
                <span class="emoji">{{ section.emoji }}</span>
              </h2>
              <p>{{ section.subtitle }}</p>
            </div>
          </div>

          <div class="task-list">
            <article
              v-for="item in section.items"
              :key="item.id"
              class="task-card"
              :class="{ completed: completedItems.includes(item.id) }"
              @click="toggleTask(item.id)"
            >
              <div
                class="task-check"
                :class="{ checked: completedItems.includes(item.id) }"
              >
                <span v-if="completedItems.includes(item.id)">✓</span>
              </div>

              <div class="task-content">
                <h3>{{ item.title }}</h3>
                <p>{{ item.description }}</p>
              </div>
            </article>
          </div>
        </div>

        <router-link to="/" class="back-home-btn">
          <span>←</span>
          <span>Back to Home</span>
        </router-link>

        <div class="closing-banner">
          <img
            src="../assets/images/recommendations-footer-bg.jpg"
            alt="Child playing"
            class="closing-bg"
          />
          <div class="closing-overlay"></div>

          <div class="closing-content">
            <div class="closing-heart">♡</div>
            <div>
              <h2>{{ page.footerCard.title }}</h2>
              <p>{{ page.footerCard.text }}</p>
              <p>{{ page.footerCard.closingLine }}</p>
            </div>
          </div>
        </div>

        <p v-if="error" class="error-text">{{ error }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const completedItems = ref([])
const error = ref('')

const page = ref({
  heroTitle: 'Your action plan for today',
  heroSubtitle: 'Simple steps to keep your child safe and comfortable',
  supportCard: {
    title: "You've got this 💚",
    text: "These aren't strict rules—they're gentle suggestions based on today's conditions. Check off actions as you go, and trust your instincts. You know your child best.",
  },
  sections: [],
  footerCard: {
    title: 'Every child is unique',
    text: "These are gentle guidelines based on today's environmental conditions in Melbourne. Always follow your child's personal asthma action plan, trust your parental instincts, and don't hesitate to reach out to your healthcare provider if you have concerns or if symptoms worsen.",
    closingLine: "You're doing a great job taking care of your child. 💛",
  },
})

const buildRecommendationsUrl = () => {
  const baseUrl =
    import.meta.env.VITE_API_BASE_URL ||
    'https://3z3kc4xlji.execute-api.ap-southeast-2.amazonaws.com'

  return `${baseUrl.replace(/\/$/, '')}/get-recommendations?location=melbourne`
}

const toggleTask = (id) => {
  if (completedItems.value.includes(id)) {
    completedItems.value = completedItems.value.filter((item) => item !== id)
  } else {
    completedItems.value.push(id)
  }
}

const fetchRecommendations = async () => {
  try {
    error.value = ''

    const res = await fetch(buildRecommendationsUrl())
    const data = await res.json()

    if (!res.ok || !data.ok) {
      throw new Error(data.message || `Request failed with status ${res.status}`)
    }

    page.value = {
      heroTitle: data.heroTitle || 'Your action plan for today',
      heroSubtitle:
        data.heroSubtitle || 'Simple steps to keep your child safe and comfortable',
      supportCard: {
        title: data.supportCard?.title || "You've got this 💚",
        text:
          data.supportCard?.text ||
          "These aren't strict rules—they're gentle suggestions based on today's conditions.",
      },
      sections: data.sections || [],
      footerCard: {
        title: data.footerCard?.title || 'Every child is unique',
        text:
          data.footerCard?.text ||
          "These are gentle guidelines based on today's environmental conditions in Melbourne.",
        closingLine:
          data.footerCard?.closingLine ||
          "You're doing a great job taking care of your child. 💛",
      },
    }
  } catch (err) {
    console.error('Failed to load recommendations:', err)
    error.value = err.message || 'Could not load recommendations right now.'
  }
}

onMounted(fetchRecommendations)
</script>

<style scoped>
.recommendations-page {
  background: var(--bg-page);
  min-height: 100vh;
}

.recommendations-hero {
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
  max-width: 620px;
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

.recommendations-content {
  padding-top: 56px;
}

.support-banner {
  position: relative;
  min-height: 290px;
  border-radius: 30px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  margin-bottom: 56px;
}

.support-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.support-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(8, 150, 123, 0.86),
    rgba(8, 150, 123, 0.74)
  );
}

.support-content {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 22px;
  align-items: flex-start;
  color: white;
  padding: 52px 48px;
  max-width: 980px;
}

.support-icon {
  font-size: 42px;
  line-height: 1;
}

.support-content h2 {
  margin: 0 0 14px;
  font-size: 38px;
  font-weight: 500;
}

.support-content p {
  margin: 0;
  font-size: 18px;
  line-height: 1.8;
}

.recommendation-group {
  margin-bottom: 56px;
}

.group-heading {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 26px;
}

.group-icon {
  width: 56px;
  height: 56px;
  min-width: 56px;
  border-radius: 18px;
  background: #d8f4e9;
  color: #0f8b70;
  display: grid;
  place-items: center;
  font-size: 28px;
  box-shadow: var(--shadow-soft);
}

.group-heading h2 {
  margin: 0 0 6px;
  font-size: 34px;
  font-weight: 500;
  color: var(--text-dark);
}

.group-heading p {
  margin: 0;
  color: var(--text-muted);
  font-size: 18px;
}

.emoji {
  font-size: 28px;
}

.task-list {
  display: grid;
  gap: 22px;
}

.task-card {
  background: white;
  border-radius: 24px;
  box-shadow: var(--shadow-soft);
  padding: 30px 32px;
  display: flex;
  gap: 24px;
  align-items: flex-start;
  cursor: pointer;
  transition: 0.2s ease;
  border: 1px solid transparent;
}

.task-card:hover {
  transform: translateY(-1px);
}

.task-card.completed {
  border-color: #b7ead6;
  box-shadow: 0 12px 28px rgba(16, 154, 126, 0.14);
}

.task-check {
  width: 38px;
  height: 38px;
  min-width: 38px;
  border-radius: 50%;
  border: 3px solid #c7ccd5;
  display: grid;
  place-items: center;
  color: white;
  font-weight: 700;
  font-size: 16px;
  margin-top: 2px;
}

.task-check.checked {
  background: #0ca57a;
  border-color: #0ca57a;
}

.task-content h3 {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 500;
  color: var(--text-dark);
}

.task-content p {
  margin: 0;
  color: var(--text-muted);
  font-size: 17px;
  line-height: 1.7;
}

.back-home-btn {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: white;
  color: #344150;
  border-radius: 999px;
  padding: 18px 32px;
  box-shadow: var(--shadow-soft);
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 64px;
}

.closing-banner {
  position: relative;
  min-height: 300px;
  border-radius: 30px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  border: 1px solid #f0d68d;
}

.closing-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.closing-overlay {
  position: absolute;
  inset: 0;
  background: rgba(247, 241, 223, 0.9);
}

.closing-content {
  position: relative;
  z-index: 2;
  display: flex;
  gap: 22px;
  align-items: flex-start;
  padding: 48px;
  max-width: 1050px;
}

.closing-heart {
  color: #ff6882;
  font-size: 46px;
  line-height: 1;
}

.closing-content h2 {
  margin: 0 0 16px;
  font-size: 36px;
  font-weight: 500;
  color: var(--text-dark);
}

.closing-content p {
  margin: 0 0 18px;
  color: #556273;
  font-size: 18px;
  line-height: 1.8;
}

.error-text {
  margin-top: 24px;
  color: #c0392b;
  font-size: 16px;
}

@media (max-width: 992px) {
  .hero-copy h1 {
    font-size: 54px;
  }

  .support-content,
  .closing-content {
    padding: 34px 28px;
  }
}

@media (max-width: 768px) {
  .recommendations-hero {
    padding: 40px 0 56px;
  }

  .brand-left {
    flex-wrap: wrap;
  }

  .hero-copy h1 {
    font-size: 42px;
    max-width: 100%;
  }

  .hero-copy p {
    font-size: 18px;
  }

  .support-content,
  .closing-content {
    flex-direction: column;
  }

  .support-content h2,
  .closing-content h2 {
    font-size: 28px;
  }

  .group-heading h2 {
    font-size: 26px;
  }

  .group-heading p,
  .task-content p {
    font-size: 16px;
  }

  .task-card {
    padding: 22px;
    gap: 18px;
  }

  .back-home-btn {
    font-size: 16px;
    padding: 16px 24px;
  }
}
</style>