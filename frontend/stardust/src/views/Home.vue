<script setup lang="ts">
import ServersList from '@/components/ServersList.vue'
import { useCurrentOsStore } from '@/stores/currentOsStore'

// const currentOsStore = useCurrentOsStore()
</script>

<template>
  <body class="bg-bg-secondary h-screen p-4">
    <!-- <div class="text-right text-lg text-text-primary mb-4">
      Current OS: {{ currentOsStore.currentOs === 'mac' ? 'macOS' : 'Windows' }}
    </div> -->
    <ServersList />
  </body>
</template>

<style scoped></style>
