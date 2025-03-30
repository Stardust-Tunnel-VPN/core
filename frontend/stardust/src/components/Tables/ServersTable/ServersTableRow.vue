<script setup lang="ts">
import { defineProps, defineEmits, computed, ref } from 'vue'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'

const props = defineProps<{
  server: IVpnServerResponse
}>()

const emit = defineEmits<{
  (e: 'connect', server: IVpnServerResponse): void
}>()

const isServerModalOpen = ref(false)

const onRowClick = (row: IVpnServerResponse) => {
  emit('connect', row)
  console.log('Server connected')
  // copy the full row info to the modal
  isServerModalOpen.value = true
}

const formattedSpeed = computed(() => {
  const speed = Number(props.server.Speed)
  if (isNaN(speed)) return props.server.Speed
  const mbSec = (speed / 1e6).toFixed(2)
  return `${mbSec} Mb/sec`
})

const formattedPing = computed(() => {
  const ping = Number(props.server.Ping)
  if (isNaN(ping)) return props.server.Ping
  return `${ping} ms`
})

const formattedUptime = computed(() => {
  const uptime = Number(props.server.Uptime)
  if (isNaN(uptime)) return props.server.Uptime
  const days = Math.floor(uptime / 86400)
  const hours = Math.floor((uptime % 86400) / 3600)
  const minutes = Math.floor((uptime % 3600) / 60)
  return `${days}d ${hours}h ${minutes}m`
})
</script>

<template>
  <tr @click="onRowClick(props.server)" class="hover:bg-bg-hover cursor-pointer">
    <td
      class="text-center px-2 py-1 border-t border-b border-border-primary text-text-primary text-md font-mono truncate"
      :title="props.server['#HostName']"
    >
      {{ props.server['#HostName'] }}
    </td>
    <td
      class="text-center px-2 py-1 border-t border-b border-border-primary text-text-primary text-md font-mono truncate"
      :title="props.server.CountryLong"
    >
      {{ props.server.CountryLong }}
    </td>
    <td
      class="text-center px-2 py-1 border-t border-b border-border-primary text-text-primary text-xs font-mono truncate"
      :title="props.server.Speed"
    >
      {{ formattedSpeed }}
    </td>
    <td
      class="text-center px-2 py-1 border-t border-b border-border-primary text-text-primary text-xs font-mono truncate"
      :title="props.server.Ping"
    >
      {{ formattedPing }}
    </td>
    <td
      class="text-center px-2 py-1 border-t border-b border-border-primary text-text-primary text-xs font-mono truncate"
      :title="props.server.Uptime"
    >
      {{ formattedUptime }}
    </td>
    <td
      class="text-center px-2 py-1 border-t border-b border-border-primary text-text-primary text-md font-mono truncate"
      :title="props.server.TotalUsers"
    >
      {{ props.server.TotalUsers }}
    </td>
  </tr>
</template>

<style scoped></style>
