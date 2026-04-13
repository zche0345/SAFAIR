import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/homepage.vue'
import InsightsPage from '../pages/InsightsPage.vue'
import RecommendationsPage from '../pages/RecommendationsPage.vue'

import ConstructionDustPage from '../pages/ConstructionDustPage.vue'

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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router