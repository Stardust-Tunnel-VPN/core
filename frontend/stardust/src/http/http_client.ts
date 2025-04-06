import axios from 'axios'
import type { AxiosInstance } from 'axios'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import { useConnectionLogsStore } from '@/stores/connectionLogsStore'
import { useCurrentOsStore } from '@/stores/currentOsStore'
import toastr from 'toastr'

/**
 * StardustHttpClient.ts
 *
 * HTTP client for interacting with the VPN API (Stardust Tunnel).
 * Default base URL: http://127.0.0.1:8000
 * Each method directly uses axios for sending HTTP requests with async/await.
 */

export interface getServersQueryParams {
  search?: string
  sortBy?: string
  sortDirection?: SortDirection
}

export enum SortDirection {
  ASC = 'ASC',
  DESC = 'DESC',
}

export class StardustHttpClient {
  private axiosInstance: AxiosInstance

  constructor(baseUrl: string = '/api/v1') {
    this.axiosInstance = axios.create({
      baseURL: baseUrl,
    })
  }

  /**
   * Connects to the VPN server.
   * @param serverIp - The VPN server IP or hostname (optional).
   * @param killSwitchEnabled - Whether to enable the kill switch (default: false).
   * @returns A string indicating the result of the connection attempt.
   */
  async connectToVpn(serverIp?: string, killSwitchEnabled: boolean = false): Promise<string> {
    const logsStore = useConnectionLogsStore()
    try {
      const params = {
        server_ip: serverIp,
        kill_switch_enabled: killSwitchEnabled.toString(),
      }

      const response = await this.axiosInstance.post<string>('/connect', null, { params })

      logsStore.addLog(response.data)

      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        toastr.error(
          `Failed to connect to the server: ${error.response.data.error}`,
          'Connection Error',
        )
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      logsStore.addLog(`Failed to connect to the server`)
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Disconnects from the VPN server.
   * @param serverIp - The VPN server IP or hostname (optional).
   * @returns A string indicating the result of the disconnection attempt.
   */
  async disconnectFromVpn(serverIp?: string): Promise<string> {
    const logsStore = useConnectionLogsStore()
    try {
      const params = {
        server_ip: serverIp,
      }
      const response = await this.axiosInstance.post<string>('/disconnect', null, { params })
      logsStore.addLog(`Disconnected from the VPN connection`)
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      logsStore.addLog(`Failed to disconnect from the VPN connection`)
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Checks the current VPN status.
   * @returns A string with the current VPN status.
   */
  async checkVpnStatus(): Promise<string> {
    const logsStore = useConnectionLogsStore()
    try {
      const response = await this.axiosInstance.get<string>('/status')
      logsStore.addLog('Checked VPN status')
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      logsStore.addLog('Failed to check VPN status')
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  async storeSudoPassword(sudoPassword: string): Promise<string> {
    const logsStore = useConnectionLogsStore()
    const osStore = useCurrentOsStore()
    if (osStore.currentOs === 'mac') {
      try {
        const response = await this.axiosInstance.post<string>('/store_sudo_password', {
          sudo_password: sudoPassword,
        })
        logsStore.addLog('Stored sudo password')
        return response.data
      } catch (error: unknown) {
        if (axios.isAxiosError(error) && error.response) {
          throw new Error(
            `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
          )
        }
        logsStore.addLog('Failed to store sudo password')
        throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    } else {
      logsStore.addLog('Sudo password storage is not supported on this OS')
      throw new Error('Sudo password storage is not supported on this OS')
    }
  }

  /**
   * Enables the kill switch.
   * @returns A string indicating the result of the operation.
   */
  async enableKillSwitch(): Promise<string> {
    const logsStore = useConnectionLogsStore()
    try {
      const response = await this.axiosInstance.post<string>('/enable_kill_switch')
      logsStore.addLog('Enabled kill switch')
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      logsStore.addLog('Failed to enable kill switch')
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Disables the kill switch.
   * @returns A string indicating the result of the operation.
   */
  async disableKillSwitch(): Promise<string> {
    const logsStore = useConnectionLogsStore()
    try {
      const response = await this.axiosInstance.post<string>('/disable_kill_switch')
      logsStore.addLog('Disabled kill switch')
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      logsStore.addLog('Failed to disable kill switch')
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Retrieves a list of VPN servers.
   * @param search - Search query (optional).
   * @param sortBy - Field to sort by (optional).
   * @param orderBy - Sort order (ASC or DESC, default: ASC).
   * @returns An array of VPN server objects.
   */
  async getVpnServers(
    search?: string,
    sortBy?: string,
    orderBy: SortDirection = SortDirection.ASC,
  ): Promise<IVpnServerResponse[]> {
    const logsStore = useConnectionLogsStore()
    try {
      const params = {
        search,
        sort_by: sortBy,
        order_by: orderBy,
      }
      const response = await this.axiosInstance.get<IVpnServerResponse[]>('/vpn_servers_list', {
        params,
      })
      logsStore.addLog('Retrieved VPN servers list')
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      logsStore.addLog('Failed to retrieve VPN servers list')
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
}
