<script setup lang="ts">
import { defineProps, defineEmits, computed, ref } from 'vue'
import type { IVpnServerResponse } from '@/utils/interfaces/vpn_servers_response'
import VModal from '@/components/Tables/Modals/VModal.vue'
import Button from '@/components/Buttons/Button.vue'
import MacInfoModal from '@/components/Tables/Modals/MacInfoModal.vue'
import { useCurrentOsStore } from '@/stores/currentOsStore'
import toastr from 'toastr'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const onClose = () => {
  emit('update:visible', false)
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
      v-if="props.visible"
      :visible="props.visible"
      headerText="Servers Fetching Warning"
      subheaderText="Please read this important information!"
      @update:visible="onClose"
    >
      <div>
        <h2 class="text-xl font-bold text-text-primary mb-4">Attention! ⚠️</h2>
        <div
          class="bg-yellow-100 border border-yellow-300 rounded-lg p-6 text-yellow-800 text-justify overflow-y-auto max-h-[600px]"
        >
          <p>
            The current fetching of free servers is powered by the academic project
            <a href="https://www.vpngate.net" target="_blank" class="font-bold">vpngate.net</a>
            – volunteers from around the world (mostly from Asian countries), including myself, are
            "transforming" their PCs into free servers that anyone can connect to. According to the
            project developers, they monitor security – and it genuinely seems to be the case.
          </p>
          <p class="mt-4">
            However, always exercise caution – you never truly know how thoroughly traffic
            interception is configured on the server you connect to. In fact, even paid VPN
            solutions don’t guarantee complete anonymity, so this is pretty normal! 🙂
          </p>
          <p class="mt-4">
            --- <strong>Note:</strong> In this MVP version, some servers fetched from vpngate.net
            unfortunately do not support the L2TP protocol. This issue lies on the vpngate.net side
            – they lack clear indicators to determine if a server supports L2TP connections, and
            some volunteers are too lazy to open their servers to L2TP because it requires extra
            steps 🙂. (We’ll need to create our own scraper to address this, and we plan to work on
            that in upcoming updates.) Third-party developers have already raised this issue on
            their forums, but it appears that the developers of this academic project have yet to
            fix it, possibly opting not to worry about it. There’s nothing we can do about it for
            now.
          </p>
          <p class="mt-4">
            <strong>What to expect soon:</strong>
            <br />
            - A new web scraper that accurately identifies L2TP servers from vpngate.net 🔍
            <br />
            - Additional sources offering free VPN connections 🌐
            <br />
            - An enhanced frontend featuring a new world map component displaying servers and
            connection options 🗺️
            <br />
            - Real-time load statistics for these free servers, so you can determine the best server
            to connect to for optimal performance 📊
          </p>
          <p class="mt-4 italic">
            Our goal is to create a free VPN client that you don’t have to pay for!
          </p>
        </div>
      </div>
      <div class="flex justify-end pt-4">
        <Button @click="onClose" text="Got it! 👍" is-active-button />
      </div>
    </VModal>
  </transition>
</template>

<style scoped></style>
