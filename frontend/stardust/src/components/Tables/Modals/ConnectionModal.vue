<script setup lang="ts">
import { defineProps, defineEmits, ref, computed } from 'vue'
import { StardustHttpClient } from '@/http/http_client'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import Button from '@/components/Buttons/Button.vue'
import Icon from '@/components/Icon.vue'
import { useConnectionStatusStore } from '@/stores/connectionStatusStore'
import KillSwitchToggle from '@/components/KillSwitchToggle.vue'

enum ConnectionMessages {
  CONNECT = 'Do you want to connect to MyL2TP Connection?',
  DISCONNECT = 'Do you want to disconnect from MyL2TP Connection?',
}

const props = defineProps<{
  serverIp?: string
  killSwitchEnabled?: boolean
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'connect', server: IVpnServerResponse | undefined): void
  (e: 'update:visible', value: boolean): void
  (e: 'update:killSwitchEnabled', value: boolean): void
}>()

const httpClient = new StardustHttpClient()
const connectionStatus = useConnectionStatusStore()

const reactiveText = ref<string>(ConnectionMessages.CONNECT)

const killSwitch = computed<boolean>({
  get: () => props.killSwitchEnabled ?? false,
  set: (val: boolean) => {
    emit('update:killSwitchEnabled', val)
  },
})

const isConnected = computed(() => connectionStatus.connected)

async function performOperation(
  operation: () => Promise<string>,
  pendingMessage: string,
  successMessage: string,
  failurePrefix: string,
  delay: number,
) {
  reactiveText.value = pendingMessage
  try {
    await operation()
    reactiveText.value = successMessage
  } catch (error) {
    reactiveText.value =
      failurePrefix + ' ' + (error instanceof Error ? error.message : String(error))
  } finally {
    await connectionStatus.getVpnConnectionStatus()
    setTimeout(() => {
      onClose()
      reactiveText.value = isConnected.value
        ? ConnectionMessages.DISCONNECT
        : ConnectionMessages.CONNECT
    }, delay)
  }
}

async function connectToMyL2TP(serverIp?: string) {
  await performOperation(
    () => httpClient.connectToVpn(serverIp, killSwitch.value),
    'Connecting...',
    'Connected successfully! ✅',
    'Failed to connect! ❌',
    5000,
  )
}

async function disconnectFromMyL2TP() {
  await performOperation(
    () => httpClient.disconnectFromVpn(),
    'Disconnecting...',
    'Disconnected successfully! ✅',
    'Failed to disconnect! ❌',
    5000,
  )
}

function onClose() {
  emit('update:visible', false)
}
</script>

<template>
  <transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <div v-if="visible" class="fixed inset-0 z-[10000] flex items-center justify-center">
      <!-- Overlay -->
      <div class="absolute inset-0 bg-black opacity-50"></div>
      <div
        class="relative bg-bg-primary rounded-lg p-6 max-w-md w-full max-h-[600px] overflow-y-auto scrollbar-dark"
      >
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-bold text-text-primary">Connection</h2>
          <button @click="onClose" class="text-text-primary cursor-pointer">
            <Icon name="close" class="w-6 h-6" />
          </button>
        </div>
        <div class="mt-3">
          <p v-if="serverIp" class="text-text-secondary text-md">
            {{
              isConnected
                ? 'Do you want to disconnect from ' + serverIp + '?'
                : 'Do you want to connect to ' + serverIp + '?'
            }}
          </p>
          <p v-else class="text-text-secondary text-md">
            {{ reactiveText }}
          </p>
          <!-- Kill Switch Toggle -->
          <div class="flex items-center justify-between mt-4">
            <span class="text-text-primary text-xl font-semibold font-source-code-pro"
              >Kill Switch feature</span
            >
            <KillSwitchToggle v-model="killSwitch" />
          </div>
          <div
            v-show="killSwitch"
            class="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-yellow-800 text-sm"
          >
            ⚠️ Attention! Although we're working on optimizing the kill-switch feature, we can't
            guarantee that enabling it will improve your connection speed. We strive to optimize and
            bypass various issues, but every OS update brings its own challenges. On macOS, it
            usually works fine, but on Windows, there might be occasional speed drops. We're on it –
            thank you for your understanding!
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <Button
              v-if="!isConnected"
              @click="connectToMyL2TP(serverIp)"
              text="Connect"
              is-active-button
            />
            <Button v-else @click="disconnectFromMyL2TP" text="Disconnect" is-active-button />
            <Button @click="onClose" text="Cancel" />
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped></style>
