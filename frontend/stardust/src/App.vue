<script setup lang="ts">
import { onMounted } from 'vue'

import Navbar from '@/components/Navbar.vue'
import Home from '@/views/Home.vue'
import { useConnectionStatusStore } from '@/stores/connectionStatusStore'
import { useCurrentOsStore } from '@/stores/currentOsStore'

const connectionStatusStore = useConnectionStatusStore()
const currentOsStore = useCurrentOsStore()

onMounted(() => {
  connectionStatusStore.getVpnConnectionStatus()
  currentOsStore.detectOs()
})
</script>

<template>
  <div>
    <Navbar showLogo />
    <Home :currentOs="currentOsStore.currentOs" />
  </div>
</template>

<style scoped></style>
