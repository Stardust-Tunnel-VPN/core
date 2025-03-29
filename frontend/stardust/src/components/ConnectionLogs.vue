<script setup lang="ts">
import Frame from '@/components/Frame.vue'
import { ref, computed } from 'vue'

// TODO: 1. Import logs-store; Use logs-store to get logs

const logs = ref<string[]>([])

const logsText = computed(() => {
  logs ? logs.value : 'No logs available'
})
</script>

<template>
  <div
    class="w-full max-w-[315px] h-full max-h-[190px] bg-logs-primary flex flex-col items-center justify-start p-4 rounded-md overflow-y-auto"
  >
    <span class="text-text-secondary text-xl font-bold font-source-code-pro"
      >Connection Logs...</span
    >
    <span class="text-text-secondary text-lg font-source-code-pro">{{ logsText }}</span>
  </div>
</template>

<style scoped></style>
