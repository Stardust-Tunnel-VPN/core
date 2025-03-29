import { defineStore } from 'pinia'
import { StardustHttpClient } from '@/http/http_client'
import { SortDirection } from '@/http/http_client'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'

interface ServersState {
  servers: IVpnServerResponse[]
  loading: boolean
  error: string | null
}

const httpClient = new StardustHttpClient()

export const useVpnServersStore = defineStore('vpnServers', {
  state: (): ServersState => ({
    servers: [],
    loading: false,
    error: null,
  }),

  getters: {
    sortedServers: (state) => (direction: SortDirection) => {
      return state.servers.sort((a, b) => {
        if (direction === SortDirection.ASC) {
          return a['#HostName'].localeCompare(b['#HostName'])
        }
        return b['#HostName'].localeCompare(a['#HostName'])
      })
    },
  },

  actions: {
    async fetchServers() {
      this.loading = true
      this.error = null

      try {
        this.servers = await httpClient.getVpnServers()
      } catch (error: unknown) {
        if (error instanceof Error) {
          this.error = error.message
        } else {
          this.error = String(error)
        }
      } finally {
        this.loading = false
      }
    },
  },
})
