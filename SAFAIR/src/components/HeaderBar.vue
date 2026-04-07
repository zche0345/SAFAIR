<template>
  <header class="header">
    <div class="container header-inner">
      <div class="brand">
        <div class="brand-icon">✦</div>
        <span>SAFAIR</span>
      </div>

      <nav class="nav">
        <a href="#home">Home</a>
        <a href="#today">Today</a>
        <a href="#about">About</a>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(0, 3, 2, 0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-inner {
  height: 78px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.brand-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.95);
  color: #0a9e93;
  display: grid;
  place-items: center;
  font-size: 14px;
  font-weight: 700;
}

.nav {
  display: flex;
  gap: 24px;
}

.nav a {
  color: rgba(255, 255, 255, 0.88);
  font-size: 15px;
}

.nav a:hover {
  color: white;
}

@media (max-width: 768px) {
  .nav {
    display: none;
  }
}
</style>