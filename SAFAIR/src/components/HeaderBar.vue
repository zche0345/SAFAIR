<template>
  <header class="app-navbar">
    <div class="container navbar-inner">
      <router-link to="/" class="navbar-brand">
        <div class="brand-icon">✦</div>
        <span class="brand-name">SAFAIR</span>
      </router-link>

      <nav class="navbar-links">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/insights" class="nav-link">Insights</router-link>
        <router-link to="/construction-dust" class="nav-link">Alerts</router-link>
        <router-link to="/recommendations" class="nav-link">Recommendations</router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
</script>

<style scoped>
.app-navbar {
  background: #ffffff;
  border-bottom: 1px solid #eceff3;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  position: sticky;
  top: 0;
  z-index: 30;
}

.navbar-inner {
  min-height: 92px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
}

.brand-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, #12b99d, #0aa16f);
  color: white;
  display: grid;
  place-items: center;
  font-size: 18px;
  box-shadow: 0 10px 20px rgba(18, 185, 157, 0.18);
}

.brand-name {
  font-size: 22px;
  font-weight: 500;
  color: #1f2430;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-link {
  text-decoration: none;
  color: #445062;
  font-size: 16px;
  font-weight: 600;
  padding: 14px 20px;
  border-radius: 16px;
  transition: 0.2s ease;
}

.nav-link:hover {
  background: #f4f8f7;
}

.nav-link.router-link-active {
  background: #e9f4f2;
  color: #007f72;
}

@media (max-width: 992px) {
  .navbar-inner {
    flex-direction: column;
    justify-content: center;
    padding: 18px 0;
  }
}

@media (max-width: 768px) {
  .navbar-links {
    flex-wrap: wrap;
    justify-content: center;
  }

  .nav-link {
    padding: 12px 16px;
    font-size: 15px;
  }

  .brand-name {
    font-size: 20px;
  }
}
</style>