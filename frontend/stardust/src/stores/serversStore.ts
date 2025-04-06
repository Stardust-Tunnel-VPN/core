import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import { SortDirection } from '@/http/http_client'
import { StardustHttpClient } from '@/http/http_client'
import { defineStore } from 'pinia'

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
    async fetchServers(search?: string, sortBy?: string, sortDirection?: SortDirection) {
      this.loading = true
      this.error = null

      try {
        this.servers = await httpClient.getVpnServers(search, sortBy, sortDirection)
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
