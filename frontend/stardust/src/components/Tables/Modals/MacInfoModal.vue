<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import Button from '@/components/Buttons/Button.vue'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

function onGotIt() {
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
      <!-- Modal container с overflow-y и скрытой полосой прокрутки -->
      <div
        class="relative bg-bg-primary rounded-lg p-6 max-w-md w-full max-h-[600px] overflow-y-auto scrollbar-dark"
      >
        <h2 class="text-2xl font-bold text-text-primary mb-4">
          🚨 Important message for macOS users!
        </h2>
        <p class="text-md text-text-secondary mb-4">
          Because Apple blocks developers from programmatically creating L2TP-VPN connections, you
          will need to set it up manually. This should only take 3-5 minutes. Once done, to switch
          servers, simply update the copied server IP and click Connect. We apologize for the
          inconvenience and understand you'd prefer a one-click solution. (By the way, this issue
          does not exist on Windows!) 😊
        </p>
        <p class="text-md text-text-secondary mb-4">
          Please follow these steps: 📝
          <br />
          - Open System Settings and go to "Network" ⚙️
          <br />
          - Click on the "VPN" tab 📡
          <br />
          - Create a VPN configuration (L2TP via IPSec) 🔒
          <br />
          - Ensure "Send all traffic through VPN" is checked ✅
          <br />
          - Create a connection named "MyL2TP" (this name is required) 🖋️
          <br />
          - Enter the desired server IP in the "Server Address" field 🌍
          <br />
          - For Account, Password, and Shared Key, use 'vpn' value 🔑
        </p>
        <p class="text-md text-text-secondary mb-4">
          In case you don't understand the algorithm, please check the detailed video below. If you
          still have any questions, feel free to contact our support team. We are always happy to
          help you! 🤗
        </p>
        <div class="mb-4">
          <img alt="Instructional GIF" class="w-full object-contain" src="" />
        </div>
        <div class="flex justify-end">
          <Button @click="onGotIt" text="Got it! 👍" is-active-button />
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
</style>
