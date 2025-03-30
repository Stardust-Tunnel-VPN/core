<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import type { IVTableHeaders } from '@/utils/interfaces/vtable_headers'
import VTable from '@/components/Tables/VTable.vue'
import ServersTableRow from '@/components/Tables/ServersTable/ServersTableRow.vue'

const props = defineProps<{
  servers: IVpnServerResponse[]
  isLoading?: boolean
}>()

// I'm not sure if they're all sortable.
const tableHeaders: IVTableHeaders[] = [
  { key: '#HostName', label: 'Server Name', sortable: false },
  { key: 'CountryLong', label: 'Country', sortable: true },
  { key: 'Speed', label: 'Speed', sortable: true },
  { key: 'Ping', label: 'Ping', sortable: true },
  { key: 'Uptime', label: 'Uptime', sortable: true },
  { key: 'TotalUsers', label: 'Total Users', sortable: true },
]
</script>

<template>
  <VTable :headers="tableHeaders" :data="props.servers">
    <template #body>
      <ServersTableRow
        v-if="!isLoading"
        v-for="server in servers"
        :key="server['#HostName']"
        :server="server"
      />
    </template>
  </VTable>
</template>

<style scoped></style>
