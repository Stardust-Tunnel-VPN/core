<script setup lang="ts">
import Frame from '@/components/Frame.vue'
import ConnectionLogs from '@/components/ConnectionLogs.vue'
import ConnectionButton from '@/components/Buttons/ConnectionButton.vue'
import Input from '@/components/Input.vue'
import Dropdown from '@/components/Dropdown.vue'
import { computed, ref, defineProps, onMounted } from 'vue'
import { availableCountries } from '@/utils/interfaces/avaliable_countries'
import type { DropdownOption } from '@/utils/interfaces/dropdown_option'
import { useVpnServersStore } from '@/stores/serversStore'
import { SortDirection } from '@/http/http_client'
import ServersTable from '@/components/Tables/ServersTable/ServersTable.vue'

// search works for #HostName property for now
const searchStr = ref('')

const countriesOptions = computed<DropdownOption<string>[]>(() => {
  return Object.entries(availableCountries).map(([countryName, countryCode]: [string, string]) => ({
    id: countryCode,
    label: countryName,
    value: countryCode,
  }))
})

const selectedCountry = ref<DropdownOption<string>>()

const sortOptions: DropdownOption<string>[] = [
  { id: '1', label: 'Sort By Speed', value: 'Speed' },
  { id: '2', label: 'Sort By Ping', value: 'Ping' },
  { id: '3', label: 'Sort By Uptime', value: 'Uptime' },
]

// 'Sort by speed' should be by default
const selectedSortOption = ref<DropdownOption<string>>(sortOptions[0])

const serversStore = useVpnServersStore()

function fetchServers(search?: string, sortBy?: string, sortDirection?: SortDirection) {
  search === '' ? (search = undefined) : search
  serversStore.fetchServers(search, sortBy, sortDirection)
}

const selectedCountryValue = computed(() => selectedCountry.value?.value)

const selectedSortOptionValue = computed(() => selectedSortOption.value?.value)

onMounted(() => {
  fetchServers(searchStr.value, selectedSortOption.value.value, SortDirection.ASC)
})
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
        <div class="w-full px-5">
          <Input v-model="searchStr" />
        </div>
        <div class="flex flex-row justify-between px-6 py-2">
          <Dropdown :options="countriesOptions" placeholder="Select country" />
          <Dropdown :options="sortOptions" placeholder="Sort by" />
        </div>
        <div class="pt-10 px-5">
          <ServersTable :servers="serversStore.servers" />
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
          <ConnectionButton />
        </div>
      </Frame>
      <Frame
        size="large"
        headerText="Connection Logs"
        subheaderText="View recent connection activity"
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
