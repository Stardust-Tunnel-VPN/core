<script setup lang="ts">
import { defineProps, defineEmits, ref, computed } from 'vue'
import { StardustHttpClient } from '@/http/http_client'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import Button from '@/components/Buttons/Button.vue'
import Icon from '@/components/Icon.vue'
import { useConnectionStatusStore } from '@/stores/connectionStatusStore'
import { useCurrentOsStore } from '@/stores/currentOsStore'
import KillSwitchToggle from '@/components/KillSwitchToggle.vue'
import Input from '@/components/Input.vue'

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
const currentOs = useCurrentOsStore()

const reactiveText = ref<string>(ConnectionMessages.CONNECT)

const sudoPassword = ref<string>('')

const killSwitch = computed<boolean>({
  get: () => props.killSwitchEnabled ?? false,
  set: (val: boolean) => {
    emit('update:killSwitchEnabled', val)
  },
})

const isConnected = computed(() => connectionStatus.connected)

const isShowPasswordInput = computed(() => {
  return currentOs.currentOs === 'mac' && killSwitch.value
})

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

async function storeSudoPassword() {
  if (!sudoPassword.value) {
    return 'Please enter your sudo password!'
  }
  try {
    await httpClient.storeSudoPassword(sudoPassword.value)
    sudoPassword.value = ''
  } catch (error) {
    console.error('Error storing sudo password:', error)
  }
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
          <!-- MACOS -->
          <div v-if="currentOs.currentOs === 'mac'" class="scrollbar-hide">
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
              Attention! <br />
              ⚠️ This setting assumes you are an advanced user and at least know what a kill-switch
              is. In this MVP version of the app, we did our best to ensure the kill-switch works
              correctly without disrupting packet exchange, and it works well on macOS. However, if
              you are unsure about what it is or doubt that you need it, it's better not to use it.
              <br />
              - Make sure you have created a VPN connection named "MyL2TP" that you can connect to!
              🔗 <br />
              - A sudo password is required to properly use the Packet Filter on macOS. Ensure you
              remember your sudo password correctly; otherwise, the kill-switch connection will not
              work! <br />
              🔑 - Although we implemented a kill-switch monitor that should correctly detect and
              disable the kill-switch state, nothing in programming is guaranteed. If you notice
              that packet exchange stops unexpectedly after using this feature, run the command
              `sudo pfctl -d` in your terminal to disable the pfctl kill-switch configuration. 🚨
            </div>
            <!-- SUDO PASSWORD INPUT -->
            <div
              v-if="isShowPasswordInput"
              class="flex flex-row gap-6 items-center justify-between pt-4"
            >
              <Input
                v-model="sudoPassword"
                placeholder="Enter your sudo password"
                is-password-input
                class="w-full"
              />
              <div
                class="flex items-center justify-center w-[45px] h-[40px] border-2 border-bg-secondary bg-bg-secondary rounded-md"
              >
                <Icon
                  @click="storeSudoPassword"
                  name="check"
                  focused
                  size="large"
                  class="text-green-400"
                />
              </div>
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
          <!-- Kill Switch Toggle -->
          <!-- WINDOWS/OTHERS -->
          <div v-else class="overflow-y-auto scrollbar-dark">
            <div class="flex items-center justify-between mt-4">
              <span class="text-text-primary text-xl font-semibold font-source-code-pro"
                >Kill Switch feature</span
              >
              <KillSwitchToggle v-model="killSwitch" is-disabled />
            </div>
            <div
              class="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-yellow-800 text-sm"
            >
              Attention! Windows users, the kill-switch feature is not developed for you yet 😕. I
              simply didn’t have enough time to implement it for Windows—I’ve only managed to create
              one for macOS so far. In fact, there's a prototype that kind of works, but I haven’t
              thoroughly tested it, so I can’t guarantee its functionality at this time. Stay tuned
              for updates—everything will be available soon! 🚀
            </div>
            <!-- SUDO PASSWORD INPUT -->
            <div
              v-if="isShowPasswordInput"
              class="flex flex-row gap-6 items-baseline justify-between"
            >
              <Input
                v-model="sudoPassword"
                placeholder="Enter your sudo password"
                is-password-input
                class="w-full"
              />
              <div class="w-[45px] h-[45px] border-2 border-bg-secondary rounded-md">
                <Icon
                  @click="storeSudoPassword"
                  name="check"
                  focused
                  size="large"
                  class="border-2 border-bg-secondary rounded-md text-green-400"
                />
              </div>
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
    </div>
  </transition>
</template>

<style scoped></style>
