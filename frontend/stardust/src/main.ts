import './assets/main.css'

import { createApp, watch } from 'vue'
import { createPinia } from 'pinia'
import { useDarkModeStore } from '@/stores/darkModeStore'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const darkModeStore = useDarkModeStore()

watch(
  () => darkModeStore.darkMode,
  (isDark) => {
    const htmlEl = document.documentElement
    isDark ? htmlEl.classList.add('dark') : htmlEl.classList.remove('dark')
  },
  { immediate: true },
)

app.mount('#app')
