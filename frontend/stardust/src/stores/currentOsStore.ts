import { defineStore } from 'pinia'

export const useCurrentOsStore = defineStore('currentOs', {
  state: () => ({
    currentOs: '' as 'mac' | 'win' | '',
    macInfoAcknowledged: false,
  }),
  actions: {
    detectOs() {
      const ua = navigator.userAgent
      if (ua.indexOf('Mac') !== -1) {
        this.currentOs = 'mac'
      } else if (ua.indexOf('Win') !== -1) {
        this.currentOs = 'win'
      } else {
        this.currentOs = 'win'
      }
    },
    acknowledgeMacInfo() {
      this.macInfoAcknowledged = true
    },
  },
})
