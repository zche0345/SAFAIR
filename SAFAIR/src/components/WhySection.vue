<template>
  <section id="about" class="why-section">
    <div class="container why-grid">
      <div class="why-copy">
        <h2>Because every breath matters</h2>
        <p>
          As parents, we know how it feels to worry about triggers you can't
          see. SAFAIR brings Melbourne's environmental data together in one
          place—translated into simple, caring advice you can actually use.
        </p>
        <p>
          No medical jargon. No guesswork. Just practical guidance to help your
          child stay active, confident, and safe.
        </p>
      </div>

      <div class="why-image-wrap">
        <img
          src="../assets/images/because-family.jpeg"
          alt="Family together"
          class="why-image"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.why-section {
  background: #edf4fb;
  padding: 84px 0;
}

.why-grid {
  display: grid;
  grid-template-columns: 1fr 0.95fr;
  align-items: center;
  gap: 48px;
}

.why-copy h2 {
  margin: 0 0 24px;
  font-size: 58px;
  line-height: 1.02;
  font-weight: 500;
  max-width: 420px;
}

.why-copy p {
  margin: 0 0 20px;
  max-width: 560px;
  color: var(--text-muted);
  line-height: 1.8;
  font-size: 18px;
}

.why-image {
  width: 100%;
  max-width: 520px;
  height: 420px;
  object-fit: cover;
  border-radius: 24px;
  box-shadow: var(--shadow-soft);
}

.why-image-wrap {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 992px) {
  .why-grid {
    grid-template-columns: 1fr;
  }

  .why-copy h2 {
    font-size: 44px;
    max-width: none;
  }

  .why-image-wrap {
    justify-content: flex-start;
  }

  .why-image {
    max-width: 100%;
    height: 340px;
  }
}

@media (max-width: 768px) {
  .why-section {
    padding: 64px 0;
  }

  .why-copy h2 {
    font-size: 34px;
  }

  .why-copy p {
    font-size: 16px;
  }
}
</style>