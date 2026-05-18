<template>
  <section class="disclaimer-section">
    <div class="container">
      <div class="disclaimer-card">
        <span class="disclaimer-icon">i</span>
        <p>
          <strong>Important:</strong> BRTHEZ provides environmental guidance based on Melbourne
          conditions. Always follow your child's personal asthma action plan and consult your
          healthcare provider for medical advice.
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.disclaimer-section {
  padding: 52px;
}

.disclaimer-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  max-width: 1040px;
  margin: 0 auto;
  padding: 26px 32px;
  border: 1px solid #eadfd5;
  border-radius: 14px;
  background: #fbf7f3;
}

.disclaimer-icon {
  width: 20px;
  height: 20px;
  margin-top: 3px;
  display: grid;
  place-items: center;
  color: #6f8d89;
  border: 2px solid #9ab2af;
  border-radius: 50%;
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 900;
  font-style: italic;
  flex: 0 0 auto;
}

.disclaimer-card p {
  margin: 0;
  color: #6f8d89;
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.7;
}

.disclaimer-card strong {
  color: #22322f;
}

/* Tablet */
@media (max-width: 768px) {
  .disclaimer-section {
    padding: 36px 20px;
  }

  .disclaimer-card {
    padding: 22px 24px;
    gap: 14px;
  }

  .disclaimer-card p {
    font-size: 14px;
    line-height: 1.65;
  }
}

/* Mobile */
@media (max-width: 480px) {
  .disclaimer-section {
    padding: 28px 16px;
  }

  .disclaimer-card {
    padding: 18px;
    gap: 12px;
    border-radius: 12px;
  }

  .disclaimer-icon {
    width: 18px;
    height: 18px;
    margin-top: 4px;
    font-size: 11px;
  }

  .disclaimer-card p {
    font-size: 13px;
    line-height: 1.6;
  }
}

/* Very small phones */
@media (max-width: 360px) {
  .disclaimer-section {
    padding: 24px 12px;
  }

  .disclaimer-card {
    padding: 16px;
  }

  .disclaimer-card p {
    font-size: 12.5px;
  }
}
</style>