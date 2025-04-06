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
      console.log('VPN status response:', response)
      const isConnected = response.toLowerCase().includes('successfully')
      this.setConnected(isConnected)
    },
  },
})
