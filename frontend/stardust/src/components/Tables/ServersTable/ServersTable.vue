<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import type { IVTableHeaders } from '@/utils/interfaces/vtable_headers'
import VTable from '@/components/Tables/VTable.vue'
import ServersTableRow from '@/components/Tables/ServersTable/ServersTableRow.vue'
import ServerInfoModal from '@/components/Tables/Modals/ServerInfoModal.vue'

const props = defineProps<{
  servers: IVpnServerResponse[]
  isLoading?: boolean
}>()

const isModalOpen = ref(false)

const openModal = () => {
  isModalOpen.value = true
}

const selectedServer = ref<IVpnServerResponse | null>(null)

const onRowClick = (server: IVpnServerResponse) => {
  selectedServer.value = server
  openModal()
}

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
        @connect="onRowClick"
      />
    </template>
  </VTable>
  <!-- MODAL -->
  <ServerInfoModal
    v-if="selectedServer"
    :visible="isModalOpen"
    :server="selectedServer"
    @update:visible="isModalOpen = false"
  />
</template>

<style scoped></style>
