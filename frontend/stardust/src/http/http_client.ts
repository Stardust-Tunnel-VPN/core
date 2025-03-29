import axios from 'axios'
import type { AxiosInstance } from 'axios'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'

/**
 * StardustHttpClient.ts
 *
 * HTTP client for interacting with the VPN API (Stardust Tunnel).
 * Default base URL: http://127.0.0.1:8000
 * Each method directly uses axios for sending HTTP requests with async/await.
 */

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
    try {
      const params = {
        server_ip: serverIp,
        kill_switch_enabled: killSwitchEnabled.toString(),
      }
      const response = await this.axiosInstance.post<string>('/connect', null, { params })
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Disconnects from the VPN server.
   * @param serverIp - The VPN server IP or hostname (optional).
   * @returns A string indicating the result of the disconnection attempt.
   */
  async disconnectFromVpn(serverIp?: string): Promise<string> {
    try {
      const params = {
        server_ip: serverIp,
      }
      const response = await this.axiosInstance.post<string>('/disconnect', null, { params })
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Checks the current VPN status.
   * @returns A string with the current VPN status.
   */
  async checkVpnStatus(): Promise<string> {
    try {
      const response = await this.axiosInstance.get<string>('/status')
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Enables the kill switch.
   * @returns A string indicating the result of the operation.
   */
  async enableKillSwitch(): Promise<string> {
    try {
      const response = await this.axiosInstance.post<string>('/enable_kill_switch')
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  /**
   * Disables the kill switch.
   * @returns A string indicating the result of the operation.
   */
  async disableKillSwitch(): Promise<string> {
    try {
      const response = await this.axiosInstance.post<string>('/disable_kill_switch')
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
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
    try {
      const params = {
        search,
        sort_by: sortBy,
        order_by: orderBy,
      }
      const response = await this.axiosInstance.get<IVpnServerResponse[]>('/vpn_servers_list', {
        params,
      })
      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          `HTTP error ${error.response.status}: ${JSON.stringify(error.response.data)}`,
        )
      }
      throw new Error(`HTTP error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
}
