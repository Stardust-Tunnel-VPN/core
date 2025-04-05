<script setup lang="ts">
import Frame from '@/components/Frame.vue'
import ConnectionLogs from '@/components/ConnectionLogs.vue'
import ConnectionButton from '@/components/Buttons/ConnectionButton.vue'
import Input from '@/components/Input.vue'
import Dropdown from '@/components/Dropdown.vue'
import LoadingButton from '@/components/Buttons/LoadingButton.vue'
import { computed, ref, onMounted, defineProps } from 'vue'
import type { DropdownOption } from '@/utils/interfaces/dropdown_option'
import { useVpnServersStore } from '@/stores/serversStore'
import { SortDirection } from '@/http/http_client'
import ServersTable from '@/components/Tables/ServersTable/ServersTable.vue'
import ConnectionModal from '@/components/Tables/Modals/ConnectionModal.vue'
import type { getServersQueryParams } from '@/http/http_client'
import CurrentOS from '@/components/CurrentOS.vue'
import toastr from 'toastr'
import ServerInfoWarnModal from '@/components/Tables/Modals/ServerInfoWarnModal.vue'
import Icon from '@/components/Icon.vue'

const searchStr = ref('')
const queryParams = ref<getServersQueryParams>({})

const isConnectionModalVisible = ref(false)
const isLoading = ref<boolean>(false)
const killSwitchEnabled = ref(false)
const showServersTableWarnModal = ref(false)

const props = defineProps<{
  currentOs: string
}>()

const tableHeaders = [
  { key: '#HostName', label: 'Server Name', sortable: false },
  { key: 'CountryLong', label: 'Country', sortable: true },
  { key: 'Speed', label: 'Speed', sortable: true },
  { key: 'Ping', label: 'Ping', sortable: true },
  { key: 'Uptime', label: 'Uptime', sortable: true },
  { key: 'TotalUsers', label: 'Total Users', sortable: true },
]

const sortOptions = computed<DropdownOption<string>[]>(() =>
  tableHeaders
    .filter((header) => header.sortable)
    .map((header) => ({
      id: header.key,
      label: `Sort by ${header.label.toLowerCase()}`,
      value: header.key,
    })),
)

const sortDirectionOptions = computed<DropdownOption<string>[]>(() => [
  { id: 'asc', label: 'Order by ascending', value: SortDirection.ASC },
  { id: 'desc', label: 'Order by descending', value: SortDirection.DESC },
])

const selectedSortOptionValue = computed({
  get: () => queryParams.value.sortBy || sortOptions.value[0]?.value || '',
  set: (newVal: string) => {
    queryParams.value.sortBy = newVal
  },
})

const selectedSortDirectionValue = computed({
  get: () => queryParams.value.sortDirection || SortDirection.ASC,
  set: (newVal: SortDirection) => {
    queryParams.value.sortDirection = newVal
  },
})

const serversStore = useVpnServersStore()

async function fetchServers(search?: string, sortBy?: string, sortDirection?: SortDirection) {
  isLoading.value = true
  try {
    if (search === '') search = undefined
    await serversStore.fetchServers(search, sortBy, sortDirection)
    if (serversStore.servers.length === 0) {
      toastr.warning('No servers found for the given search criteria.')
    }
    if (serversStore.servers.length > 0) {
      toastr.success('Servers fetched successfully.')
    }
  } catch (error) {
    toastr.error('Error fetching servers. Please try again later.')
    console.error('Error fetching servers:', error)
  } finally {
    isLoading.value = false
  }
}

function onRefresh() {
  fetchServers(searchStr.value, selectedSortOptionValue.value, selectedSortDirectionValue.value)
  toastr.info('Servers refreshed successfully.')
}

function toggleConnectionModal() {
  isConnectionModalVisible.value = !isConnectionModalVisible.value
}

function toggleServersTableWarnModal() {
  showServersTableWarnModal.value = !showServersTableWarnModal.value
}

onMounted(() => {
  fetchServers(searchStr.value, selectedSortOptionValue.value, SortDirection.ASC)
})
</script>

<template>
  <div class="flex items-center justify-evenly pt-[40px] bg-green-200">
    <div class="flex justify-center">
      <!-- TABLE -->

      <div class="flex items-center px-6">
        <Frame size="table" headerText="VPN Servers" subheaderText="Choose your server">
          <div class="w-full px-5 flex items-center justify-between">
            <Input v-model="searchStr" placeholder="Search by server name..." class="w-3/4" />
            <LoadingButton :isLoading="isLoading" buttonText="Refresh" @refresh="onRefresh" />
            <Icon
              name="crisis_alert"
              @click="toggleServersTableWarnModal"
              class="text-red-500 cursor-pointer"
            />
          </div>
          <div class="flex flex-col gap-4 w-full py-7">
            <div class="flex flex-row justify-between w-full px-5">
              <Dropdown
                v-model="selectedSortOptionValue"
                :options="sortOptions"
                placeholder="Sort by"
              />
            </div>
            <div class="flex flex-row justify-between w-full px-5">
              <Dropdown
                v-model="selectedSortDirectionValue"
                :options="sortDirectionOptions"
                placeholder="Sort direction"
              />
            </div>
          </div>
          <div class="px-5 w-full">
            <ServersTable
              :servers="serversStore.servers"
              :table-headers="tableHeaders"
              :is-loading="isLoading"
            />
          </div>
        </Frame>
      </div>
    </div>
    <!-- RIGHT-SIDE  -->
    <div class="flex flex-col gap-10">
      <CurrentOS :currentOs="props.currentOs" />
      <Frame
        size="medium"
        headerText="Connection status"
        subheaderText="Monitor your VPN connection and connect"
      >
        <div class="flex flex-row justify-start px-6 py-2">
          <ConnectionButton @click="toggleConnectionModal" />
          <ConnectionModal
            v-model:visible="isConnectionModalVisible"
            v-model:kill-switch-enabled="killSwitchEnabled"
          />
        </div>
      </Frame>
      <Frame
        size="large"
        headerText="Connection Logs"
        subheaderText="Take a look at the logs of your recent actions in this strange terminal..."
      >
        <div class="w-full h-full flex items-start justify-center">
          <ConnectionLogs />
        </div>
      </Frame>
    </div>
  </div>
  <ServerInfoWarnModal
    v-if="showServersTableWarnModal"
    :visible="showServersTableWarnModal"
    @update:visible="showServersTableWarnModal = false"
  />
</template>

<style scoped></style>
