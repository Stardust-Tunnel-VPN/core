import { defineStore } from 'pinia'

interface DarkModeState {
  darkMode: boolean
}

const DARK_MODE_KEY = 'darkMode'

// Get the initial dark mode value from local storage
function getInitialDarkMode(): boolean {
  const storedValue = localStorage.getItem(DARK_MODE_KEY)
  return storedValue ? JSON.parse(storedValue) : false
}

export const useDarkModeStore = defineStore('darkMode', {
  state: (): DarkModeState => ({
    darkMode: getInitialDarkMode(),
  }),

  getters: {
    isDarkMode: (state) => state.darkMode,
  },

  actions: {
    enableDarkMode() {
      this.darkMode = true
      localStorage.setItem(DARK_MODE_KEY, JSON.stringify(this.darkMode))
    },

    disableDarkMode() {
      this.darkMode = false
      localStorage.setItem(DARK_MODE_KEY, JSON.stringify(this.darkMode))
    },

    toggleDarkMode() {
      this.darkMode = !this.darkMode
      localStorage.setItem(DARK_MODE_KEY, JSON.stringify(this.darkMode))
    },
  },
})
