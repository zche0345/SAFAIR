<script setup>
import DisclaimerBanner from './components/DisclaimerBanner.vue'
import HeaderBar from './components/HeaderBar.vue'
import SiteFooter from './components/SiteFooter.vue'
</script>

<template>
  <HeaderBar />
  <router-view />
  <DisclaimerBanner />
  <SiteFooter />

</template>

<style scoped></style>
