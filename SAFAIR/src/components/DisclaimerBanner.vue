<template>
  <section class="disclaimer-wrap">
    <div class="container">
      <div class="disclaimer">
        <span class="icon">i</span>
        <p>
          <strong>Important:</strong> BRTHEZ provides environmental guidance
          based on Melbourne conditions. Always follow your child's personal
          asthma action plan and consult your healthcare provider for medical
          advice.
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.disclaimer-wrap {
  background: #f7f7f8;
  padding: 44px 0 72px;
}

.disclaimer {
  max-width: 760px;
  margin: 0 auto;
  background: #eef4ff;
  color: #536173;
  border-radius: 18px;
  padding: 22px 24px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.icon {
  width: 22px;
  height: 22px;
  min-width: 22px;
  border-radius: 50%;
  background: white;
  color: #4670ff;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
  margin-top: 2px;
}

.disclaimer p {
  margin: 0;
  line-height: 1.7;
  font-size: 14px;
}

@media (max-width: 768px) {
  .disclaimer {
    padding: 18px;
  }
}
</style>