<script setup lang="ts">
import { defineProps, defineEmits, computed, ref } from 'vue'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import { formatSpeed, formatPing, formatUptime } from '@/utils/functions/formatters'
import { StardustHttpClient } from '@/http/http_client'
import { useConnectionStatusStore } from '@/stores/connectionStatusStore'
import VModal from '@/components/Tables/Modals/VModal.vue'
import Button from '@/components/Buttons/Button.vue'
import Icon from '@/components/Icon.vue'
import MacInfoModal from '@/components/Tables/Modals/MacInfoModal.vue'
import { useCurrentOsStore } from '@/stores/currentOsStore'

const props = defineProps<{
  visible: boolean
  server: IVpnServerResponse
  additionalInfo?: string
}>()

const emit = defineEmits<{
  (e: 'connect', server: IVpnServerResponse): void
  (e: 'update:visible', value: boolean): void
}>()

const formattedSpeed = computed(() => formatSpeed(props.server.Speed))
const formattedPing = computed(() => formatPing(props.server.Ping))
const formattedUptime = computed(() => formatUptime(props.server.Uptime))

const httpClient = new StardustHttpClient()
const connectionStatusStore = useConnectionStatusStore()
const currentOsStore = useCurrentOsStore()

const showMacInfoModal = ref(false)

if (currentOsStore.currentOs === 'mac') {
  showMacInfoModal.value = true
}

function connectToVpnServer(server: IVpnServerResponse) {
  try {
    httpClient.connectToVpn(server.IP, false)
    emit('connect', server)
  } catch (error) {
    console.error('Failed to connect to VPN server', error)
  } finally {
    connectionStatusStore.getVpnConnectionStatus()
  }
}

const onConnect = () => {
  connectToVpnServer(props.server)
}

const onClose = () => {
  emit('update:visible', false)
}

function copyToClipboard(text: string) {
  navigator.clipboard
    .writeText(text)
    .then(() => console.log('Copied to clipboard:', text))
    .catch((err) => console.error('Failed to copy:', err))
}
</script>

<template>
  <!-- MAIN MODAL -->
  <transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <VModal
      v-if="visible"
      :visible="visible"
      headerText="Server Info"
      subheaderText="Details of the selected server"
      @update:visible="onClose"
    >
      <div class="space-y-2">
        <!-- Server Name -->
        <div class="flex flex-col">
          <span class="text-xl font-bold text-text-primary">Server Name:</span>
          <div class="flex items-center justify-between pr-10">
            <span
              class="text-md font-source-code-pro text-text-primary truncate pl-3"
              :title="server['#HostName']"
            >
              {{ server['#HostName'] }}
            </span>
            <Icon
              name="content_copy"
              class="ml-2 hover:scale-105 transition-transform duration-200 cursor-pointer text-text-primary"
              @click="copyToClipboard(server['#HostName'])"
            />
          </div>
        </div>
        <!-- IP -->
        <div class="flex flex-col">
          <span class="text-xl font-bold text-text-primary">IP:</span>
          <div class="flex items-center justify-between pr-10">
            <span
              class="text-md font-source-code-pro text-text-primary truncate pl-3"
              :title="server.IP"
            >
              {{ server.IP }}
            </span>
            <Icon
              name="content_copy"
              class="ml-2 hover:scale-105 transition-transform duration-200 cursor-pointer text-text-primary"
              @click="copyToClipboard(server.IP)"
            />
          </div>
        </div>
        <!-- Country -->
        <div class="flex flex-col">
          <span class="text-xl font-bold text-text-primary">Country:</span>
          <div class="flex items-center justify-between pr-10">
            <span
              class="text-md font-source-code-pro text-text-primary truncate pl-3"
              :title="server.CountryLong"
            >
              {{ server.CountryLong }}
            </span>
            <Icon
              name="content_copy"
              class="ml-2 hover:scale-105 transition-transform duration-200 cursor-pointer text-text-primary"
              @click="copyToClipboard(server.CountryLong)"
            />
          </div>
        </div>
        <!-- Speed -->
        <div class="flex flex-col">
          <span class="text-xl font-bold text-text-primary">Speed:</span>
          <div class="flex items-center justify-between pr-10">
            <span
              class="text-md font-source-code-pro text-text-primary truncate pl-3"
              :title="formattedSpeed"
            >
              {{ formattedSpeed }}
            </span>
            <Icon
              name="content_copy"
              class="ml-2 hover:scale-105 transition-transform duration-200 cursor-pointer text-text-primary"
              @click="copyToClipboard(formattedSpeed)"
            />
          </div>
        </div>
        <!-- Ping -->
        <div class="flex flex-col">
          <span class="text-xl font-bold text-text-primary">Ping:</span>
          <div class="flex items-center justify-between pr-10">
            <span
              class="text-md font-source-code-pro text-text-primary truncate pl-3"
              :title="formattedPing"
            >
              {{ formattedPing }}
            </span>
            <Icon
              name="content_copy"
              class="ml-2 hover:scale-105 transition-transform duration-200 cursor-pointer text-text-primary"
              @click="copyToClipboard(formattedPing)"
            />
          </div>
        </div>
        <!-- Uptime -->
        <div class="flex flex-col">
          <span class="text-xl font-bold text-text-primary">Uptime:</span>
          <div class="flex items-center justify-between pr-10">
            <span
              class="text-md font-source-code-pro text-text-primary truncate pl-3"
              :title="formattedUptime"
            >
              {{ formattedUptime }}
            </span>
            <Icon
              name="content_copy"
              class="ml-2 hover:scale-105 transition-transform duration-200 cursor-pointer text-text-primary"
              @click="copyToClipboard(formattedUptime)"
            />
          </div>
        </div>
        <!-- Total Users -->
        <div class="flex flex-col">
          <span class="text-xl font-bold text-text-primary">Total Users:</span>
          <div class="flex items-center justify-between pr-10">
            <span
              class="text-md font-source-code-pro text-text-primary truncate pl-3"
              :title="server.TotalUsers"
            >
              {{ server.TotalUsers }}
            </span>
            <Icon
              name="content_copy"
              class="ml-2 hover:scale-105 transition-transform duration-200 cursor-pointer text-text-primary"
              @click="copyToClipboard(server.TotalUsers)"
            />
          </div>
        </div>
        <!-- Operator -->
        <div class="flex flex-col">
          <span class="text-xl font-bold text-text-primary">Operator:</span>
          <div class="flex items-center justify-between pr-10">
            <span
              class="text-md font-source-code-pro text-text-primary truncate pl-3"
              :title="server.Operator"
            >
              {{ server.Operator }}
            </span>
            <Icon
              name="content_copy"
              class="ml-2 hover:scale-105 transition-transform duration-200 cursor-pointer text-text-primary"
              @click="copyToClipboard(server.Operator)"
            />
          </div>
        </div>
      </div>
      <div class="flex justify-end mt-6 space-x-4">
        <Button @click="onConnect" type="primary" text="Connect" isActiveButton />
        <Button @click="onClose" type="secondary" text="Close" />
      </div>
    </VModal>
  </transition>
  <MacInfoModal
    v-model:visible="showMacInfoModal"
    v-if="currentOsStore.currentOs === 'mac' && !currentOsStore.macInfoAcknowledged"
    @update:visible="
      (val) => {
        if (!val) currentOsStore.acknowledgeMacInfo()
      }
    "
  />
</template>

<style scoped></style>
