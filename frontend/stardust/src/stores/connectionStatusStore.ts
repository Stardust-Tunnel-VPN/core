import { defineStore } from 'pinia'
import { StardustHttpClient } from '@/http/http_client'

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
      this.setConnected(response.toLowerCase() === 'connected')
    },
  },
})
