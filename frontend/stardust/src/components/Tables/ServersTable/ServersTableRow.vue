<script setup lang="ts">
import { defineProps, defineEmits, computed, ref } from 'vue'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import { formatPing, formatSpeed, formatUptime } from '@/utils/functions/formatters'

const props = defineProps<{
  server: IVpnServerResponse
}>()

const emit = defineEmits<{
  (e: 'connect', server: IVpnServerResponse): void
}>()

const onRowClick = (row: IVpnServerResponse) => {
  emit('connect', row)
  console.log('Server connected')
}

const formattedSpeed = computed(() => formatSpeed(props.server.Speed))
const formattedPing = computed(() => formatPing(props.server.Ping))
const formattedUptime = computed(() => formatUptime(props.server.Uptime))
</script>

<template>
  <tr
    @click="onRowClick(props.server)"
    class="hover:scale-102 cursor-pointer transition-transform duration-200"
  >
    <td
      class="text-center px-1 py-3 border-t border-b border-border-primary text-text-primary text-md font-mono truncate"
      :title="props.server['#HostName']"
    >
      {{ props.server['#HostName'] }}
    </td>
    <td
      class="text-center px-1 py-3 border-t border-b border-border-primary text-text-primary text-md font-mono truncate"
      :title="props.server.CountryLong"
    >
      {{ props.server.CountryLong }}
    </td>
    <td
      class="text-center px-1 py-3 border-t border-b border-border-primary text-text-primary text-xs font-mono truncate"
      :title="props.server.Speed"
    >
      {{ formattedSpeed }}
    </td>
    <td
      class="text-center px-1 py-3 border-t border-b border-border-primary text-text-primary text-xs font-mono truncate"
      :title="props.server.Ping"
    >
      {{ formattedPing }}
    </td>
    <td
      class="text-center px-1 py-3 border-t border-b border-border-primary text-text-primary text-xs font-mono truncate"
      :title="props.server.Uptime"
    >
      {{ formattedUptime }}
    </td>
    <td
      class="text-center px-1 py-3 border-t border-b border-border-primary text-text-primary text-md font-mono truncate"
      :title="props.server.TotalUsers"
    >
      {{ props.server.TotalUsers }}
    </td>
  </tr>
</template>

<style scoped></style>
