<script setup lang="ts">
import Frame from '@/components/Frame.vue'
import ConnectionLogs from '@/components/ConnectionLogs.vue'
import ConnectionButton from '@/components/Buttons/ConnectionButton.vue'
import Input from '@/components/Input.vue'
import Dropdown from '@/components/Dropdown.vue'
import { computed, ref, defineProps, onMounted, watch } from 'vue'
import { availableCountries } from '@/utils/interfaces/avaliable_countries'
import type { DropdownOption } from '@/utils/interfaces/dropdown_option'
import { useVpnServersStore } from '@/stores/serversStore'
import { SortDirection } from '@/http/http_client'
import ServersTable from '@/components/Tables/ServersTable/ServersTable.vue'
import ConnectionModal from '@/components/Tables/Modals/ConnectionModal.vue'
import { StardustHttpClient } from '@/http/http_client'
import type { getServersQueryParams } from '@/http/http_client'

// search works for #HostName property for now
const searchStr = ref('')

const queryParams = ref<getServersQueryParams>({})

const isConnectionModalVisible = ref(false)

const isLoading = ref<boolean>(false)

const tableHeaders = [
  { key: '#HostName', label: 'Server Name', sortable: false },
  { key: 'CountryLong', label: 'Country', sortable: true },
  { key: 'Speed', label: 'Speed', sortable: true },
  { key: 'Ping', label: 'Ping', sortable: true },
  { key: 'Uptime', label: 'Uptime', sortable: true },
  { key: 'TotalUsers', label: 'Total Users', sortable: true },
]

// generating sortable options based on table headers
const sortOptions = computed<DropdownOption<string>[]>(() =>
  tableHeaders
    .filter((header) => header.sortable)
    .map((header) => ({
      id: header.key,
      label: `Sort by ${header.label.toLowerCase()}`,
      value: header.key,
    })),
)

const selectedSortOptionValue = computed({
  get: () => queryParams.value.sortBy || sortOptions.value[0]?.value || '',
  set: (newVal: string) => {
    queryParams.value.sortBy = newVal
  },
})

const serversStore = useVpnServersStore()

function fetchServers(search?: string, sortBy?: string, sortDirection?: SortDirection) {
  isLoading.value = true
  try {
    search === '' ? (search = undefined) : search
    serversStore.fetchServers(search, sortBy, sortDirection)
  } finally {
    isLoading.value = false
  }
}

function toggleConnectionModal() {
  isConnectionModalVisible.value = !isConnectionModalVisible.value
}

onMounted(() => {
  fetchServers(searchStr.value, selectedSortOptionValue.value, SortDirection.ASC)
})

watch(
  queryParams,
  (newQueryParams) => {
    fetchServers(searchStr.value, newQueryParams.sortBy, SortDirection.ASC)
  },
  { deep: true },
)
</script>

<template>
  <!-- TODO: fix css divs styling -->
  <div class="flex items-center justify-evenly pt-[40px]">
    <div class="flex justify-center">
      <Frame
        size="table"
        headerText="VPN Servers"
        subheaderText="Choose your server"
        bg-color="white"
      >
        <!-- V-MODEL BASED SEARCH, 2 DROPDOWNS (V-MODEL AS WELL) + TABLE -->
        <div class="flex flex-col items-center justify-center">
          <div class="w-full px-5">
            <Input v-model="searchStr" placeholder="Search by server name..." />
          </div>
          <div class="flex flex-row justify-between w-full mt-10 px-5">
            <Dropdown
              v-model="selectedSortOptionValue"
              :options="sortOptions"
              placeholder="Sort by"
            />
          </div>
          <div class="mt-2 px-5 w-full">
            <ServersTable
              :servers="serversStore.servers"
              :table-headers="tableHeaders"
              :is-loading="isLoading"
            />
          </div>
        </div>
      </Frame>
    </div>
    <!-- TODO: make the max gap respectfully to the parent -->
    <div class="flex flex-col gap-10">
      <Frame
        size="medium"
        headerText="Connection status"
        subheaderText="Monitor your VPN connection"
        bg-color="white"
      >
        <!-- CONNECTION-STATUS BUTTON -->
        <div class="flex flex-row justify-start px-6 py-2">
          <ConnectionButton @click="toggleConnectionModal" />
          <ConnectionModal v-model:visible="isConnectionModalVisible" />
        </div>
      </Frame>
      <Frame
        size="large"
        headerText="Connection Logs"
        subheaderText="Take a look at the logs of your recent actions in this strange terminal..."
        bg-color="white"
      >
        <!-- CONNECTION-LOGS COMPONENT -->
        <div class="w-full h-full flex items-start justify-center">
          <ConnectionLogs />
        </div>
      </Frame>
    </div>
  </div>
</template>

<style scoped></style>
