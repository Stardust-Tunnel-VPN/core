import { defineStore } from 'pinia'

export const useConnectionLogsStore = defineStore('connectionLogs', {
  state: () => ({
    logs: [] as string[],
  }),
  actions: {
    addLog(log: string) {
      this.logs.push(log)
    },
  },
})
