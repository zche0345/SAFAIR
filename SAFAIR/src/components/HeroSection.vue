<template>
  <section id="home" class="hero">
    <div class="container hero-grid">
      <div class="hero-copy">
        <div class="hero-brand">
          <div class="hero-brand-icon">✦</div>
          <span>SAFAIR</span>
        </div>

        <h1>They deserve to breathe easy</h1>

        <p>
          We help Melbourne parents stay ahead of asthma triggers—so your child
          can play, learn, and thrive with confidence.
        </p>

        <router-link to="/insights" class="btn-pill btn-light hero-link-btn">
          See Today's Conditions
          <span>→</span>
        </router-link>
      </div>

      <div class="hero-image-wrap">
        <img
          src="../assets/images/hero-family.jpeg"
          alt="Children outdoors"
          class="hero-image"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  background: linear-gradient(135deg, var(--primary-teal), var(--primary));
  padding: 72px 0 76px;
  min-height: 640px;
  display: flex;
  align-items: center;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  align-items: center;
  gap: 56px;
}

.hero-brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: white;
  margin-bottom: 28px;
  font-size: 16px;
  font-weight: 500;
}

.hero-brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.96);
  color: #0a9e93;
  display: grid;
  place-items: center;
  font-size: 15px;
}

.hero-copy h1 {
  margin: 0;
  color: white;
  font-size: 68px;
  line-height: 0.98;
  font-weight: 500;
  max-width: 520px;
}

.hero-copy p {
  margin: 28px 0 34px;
  color: rgba(255, 255, 255, 0.92);
  font-size: 18px;
  line-height: 1.7;
  max-width: 560px;
}

.hero-image-wrap {
  display: flex;
  justify-content: flex-end;
}

.hero-image {
  width: 100%;
  max-width: 540px;
  height: 420px;
  object-fit: cover;
  border-radius: 24px;
  box-shadow: var(--shadow-soft);
}

@media (max-width: 992px) {
  .hero {
    min-height: auto;
    padding: 56px 0 64px;
  }

  .hero-grid {
    grid-template-columns: 1fr;
  }

  .hero-copy h1 {
    font-size: 52px;
    max-width: 100%;
  }

  .hero-image-wrap {
    justify-content: flex-start;
  }

  .hero-image {
    max-width: 100%;
    height: 360px;
  }
}

@media (max-width: 768px) {
  .hero-copy h1 {
    font-size: 40px;
    line-height: 1.04;
  }

  .hero-copy p {
    font-size: 16px;
  }

  .hero-image {
    height: 280px;
  }
}

.hero-link-btn {
  display: inline-flex;
}
</style>