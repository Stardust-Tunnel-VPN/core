<script setup lang="ts">
import { defineProps, onMounted } from 'vue'
import Loader from '@/components/Loader.vue'
import Frame from '@/components/Frame.vue'
import Icon from '@/components/Icon.vue'
import Input from '@/components/Input.vue'
import Navbar from '@/components/Navbar.vue'
import Home from '@/views/Home.vue'
import { useConnectionStatusStore } from '@/stores/connectionStatusStore'

const connectionStatusStore = useConnectionStatusStore()

onMounted(() => {
  connectionStatusStore.getVpnConnectionStatus()
})
</script>

<template>
  <div class="wrapper">
    <Navbar showLogo />
    <Home />
  </div>
</template>

<style scoped></style>
