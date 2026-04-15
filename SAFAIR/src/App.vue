<script setup>
import DisclaimerBanner from './components/DisclaimerBanner.vue'
import HeaderBar from './components/HeaderBar.vue'
</script>

<template>
  <HeaderBar />
  <router-view />
  <DisclaimerBanner />
</template>

<style scoped></style>
