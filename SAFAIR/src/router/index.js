import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import InsightsPage from '../pages/InsightsPage.vue'
import RecommendationsPage from '../pages/RecommendationsPage.vue'

import ConstructionDustPage from '../pages/ConstructionDustPage.vue'
import SafeRoutePlanning from '../pages/SafeRoutePlanning.vue'
import HousingScannerPage from '../pages/HousingScannerPage.vue'
import LearnPage from '../pages/LearnPage.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage,
  },
  {
    path: '/insights',
    name: 'insights',
    component: InsightsPage,
  },
  {
    path: '/recommendations',
    name: 'recommendations',
    component: RecommendationsPage,
  },
  {
    path: '/construction-dust',
    name: 'construction-dust',
    component: ConstructionDustPage,
  },
  {
    path: '/safe-route-planning',
    component: SafeRoutePlanning
  },
  {
    path: '/housing-scanner',
    component: HousingScannerPage
  },
  {
    path: '/asthma-learn',
    component: LearnPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router