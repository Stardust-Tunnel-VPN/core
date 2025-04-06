import './assets/main.css'
import 'toastr/build/toastr.min.css'

import { createApp, watch } from 'vue'

import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'
import toastr from 'toastr'
import { useDarkModeStore } from '@/stores/darkModeStore'

toastr.options = {
  closeButton: true,
  debug: false,
  newestOnTop: true,
  progressBar: true,
  positionClass: 'toast-top-right',
  preventDuplicates: false,
  showDuration: 300,
  hideDuration: 1000,
  timeOut: 5000,
  extendedTimeOut: 1000,
  showEasing: 'swing',
  hideEasing: 'linear',
  showMethod: 'fadeIn',
  hideMethod: 'fadeOut',
}

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
