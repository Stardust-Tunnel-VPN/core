import { StardustHttpClient } from '@/http/http_client'
import { defineStore } from 'pinia'
import { computed } from 'vue'

const isConnected = computed(() => {})

export const useConnectionStatusStore = defineStore('connectionStatus', {
  state: () => ({
    connected: false,
  }),
  actions: {
    setConnected(connected: boolean) {
      this.connected = connected
    },
    async getVpnConnectionStatus() {
      const httpClient = new StardustHttpClient()
      const response = await httpClient.checkVpnStatus()
      console.log('VPN status response:', response)
      const isConnected =
        response.toLowerCase().includes('successfully') ||
        (response.toLowerCase().includes('connected') &&
          !response.toLowerCase().includes('disconnected'))
      this.setConnected(isConnected)
    },
  },
})
