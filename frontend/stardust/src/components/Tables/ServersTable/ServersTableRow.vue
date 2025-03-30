<script setup lang="ts">
import { defineProps, ref, defineEmits } from 'vue'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'

const props = defineProps<{
  server: IVpnServerResponse
}>()
</script>

<template>
  <tr class="hover:bg-bg-hover">
    <td class="px-4 py-2 border-t border-border-primary text-text-primary">
      {{ props.server['#HostName'] }}
    </td>
    <td class="px-4 py-2 border border-border-primary text-text-primary">
      {{ props.server.CountryLong }}
    </td>
    <td class="px-4 py-2 border border-border-primary text-text-primary">
      {{ props.server.Speed }}
    </td>
    <td class="px-4 py-2 border border-border-primary text-text-primary">
      {{ props.server.Ping }}
    </td>
    <td class="px-4 py-2 border border-border-primary text-text-primary">
      {{ props.server.Uptime }}
    </td>
    <td class="px-4 py-2 border border-border-primary text-text-primary">
      {{ props.server.TotalUsers }}
    </td>
    <td class="px-4 py-2 border border-border-primary text-text-primary">
      {{ props.server.Operator }}
    </td>
  </tr>
</template>

<style scoped></style>
