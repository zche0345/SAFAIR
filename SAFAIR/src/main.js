import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/styles/index.css'
import { registerServiceWorker } from './utils/pushNotifications'

createApp(App).use(router).mount('#app')

registerServiceWorker().catch((err) => {
  console.error('Service worker registration failed', err)
})